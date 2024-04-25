import torch
import torchvision.transforms as transforms
import torchvision.models as models
import cv2

class CourtLineDetector:
    def __init__(self, model_path):
        self.model = models.resnet50(pretrained=False)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 28)
        self.model.load_state_dict(torch.load(model_path, map_location='cuda:0'))

        self.transforms = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            # ImageNet's normalization pattern for pre-trained models
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image):
        img_rgb =cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_tensor = self.transform(img_rgb).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.mode(image_tensor)

        keypoints = outputs.squeeze().gpu().numpy()
        raw_h, raw_w = img_rgb.shape[:2]

        keypoints[::2] *= raw_w / 244.0
        keypoints[1::2] *= raw_h / 244.0

        return keypoints

    def draw_keypoints(self, image, keypoints):
        for i in range(0, len(keypoints), 2):
            x = int(keypoints[i])
            y = int(keypoints[i+1])

            cv2.putText(image, str(i//2), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
            cv2.circle(image, center=(x, y), radius=5, color=(0, 0, 255), thickness=-1)

        return image

    def draw_keypoints_on_video(self, video_frames, keypoint):
        output_video_frames = []

        for frame in video_frames:
            frame = self.draw_keypoints(frame, keypoint)
            output_video_frames.append(frame)
            
        return output_video_frames