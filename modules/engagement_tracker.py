"""
Engagement Tracker Module - OpenCV based face detection
Mock interview ke during user ki engagement track karne ke liye
"""

import cv2
import numpy as np
import time
import os
from datetime import datetime
import json

class EngagementTracker:
    def __init__(self, config=None):
        """
        Initialize Engagement Tracker with OpenCV
        """
        print("🎥 Initializing Engagement Tracker...")
        
        # Default configuration
        self.config = {
            'min_engagement_time': 30,
            'face_detection_interval': 5,
            'attention_threshold': 70,
            'save_frames': False,
            'camera_id': 0
        }
        
        if config:
            self.config.update(config)
        
        # Load face detection model
        self._load_face_detector()
        
        # Initialize variables
        self.reset_metrics()
        
        # Reports folder banayein (modules folder ke andar)
        self.reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
        
        print("✅ Engagement Tracker initialized!")
        print(f"📁 Reports will be saved in: {self.reports_dir}")
        
    def _load_face_detector(self):
        """
        Load OpenCV's pre-trained face detection model
        """
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                print("⚠️ Warning: Could not load face cascade.")
                self.face_cascade = None
            else:
                print("✅ Face detector loaded successfully")
                
        except Exception as e:
            print(f"❌ Error loading face detector: {e}")
            self.face_cascade = None
    
    def reset_metrics(self):
        """
        Reset all tracking metrics
        """
        self.metrics = {
            'total_frames': 0,
            'faces_detected': 0,
            'frames_with_face': 0,
            'frames_without_face': 0,
            'engagement_score': 0,
            'attention_percentage': 0,
            'face_present_duration': 0,
            'face_absent_duration': 0,
            'session_duration': 0,
            'start_time': None,
            'end_time': None,
            'face_position_history': [],
            'attention_scores': [],
            'timestamps': []
        }
    
    def detect_face(self, frame):
        """
        Detect face in frame using Haar Cascade
        """
        if self.face_cascade is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces
    
    def calculate_attention_score(self, faces, frame_shape):
        """
        Calculate attention score based on face position
        """
        if faces is None or len(faces) == 0:
            return 0
        
        # First face le lo
        x, y, w, h = faces[0]
        frame_h, frame_w = frame_shape[:2]
        
        # Face ka center
        face_center_x = x + w//2
        face_center_y = y + h//2
        
        # Frame ka center
        frame_center_x = frame_w // 2
        frame_center_y = frame_h // 2
        
        # Calculate distance from center (normalized)
        distance_x = abs(face_center_x - frame_center_x) / (frame_w // 2)
        distance_y = abs(face_center_y - frame_center_y) / (frame_h // 2)
        
        # Euclidean distance
        distance = np.sqrt(distance_x**2 + distance_y**2)
        
        # Convert distance to score (closer to center = higher score)
        attention_score = max(0, 100 - (distance * 50))
        
        return attention_score
    
    def draw_face_box(self, frame, faces, attention_score):
        """
        Draw box around detected face with attention score
        """
        for (x, y, w, h) in faces:
            # Color based on attention score
            if attention_score > 80:
                color = (0, 255, 0)  # Green - High attention
            elif attention_score > 50:
                color = (0, 255, 255)  # Yellow - Medium attention
            else:
                color = (0, 0, 255)  # Red - Low attention
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Draw attention score
            score_text = f"Attention: {attention_score:.1f}%"
            cv2.putText(frame, score_text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def start_tracking(self, duration_seconds=60):
        """
        Start tracking engagement for specified duration
        """
        print(f"\n🎥 Starting engagement tracking for {duration_seconds} seconds...")
        print("   Press 'q' to stop early")
        print("   Look at the camera and stay engaged!")
        
        # Open camera
        cap = cv2.VideoCapture(self.config['camera_id'])
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return None
        
        # Reset metrics
        self.reset_metrics()
        self.metrics['start_time'] = time.time()
        
        frame_count = 0
        
        while True:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Could not read frame")
                break
            
            # Flip frame horizontally (mirror effect)
            frame = cv2.flip(frame, 1)
            
            # Process every nth frame (performance optimization)
            if frame_count % self.config['face_detection_interval'] == 0:
                # Detect face
                faces = self.detect_face(frame)
                
                # Update metrics
                self.metrics['total_frames'] += 1
                
                if faces is not None and len(faces) > 0:
                    self.metrics['faces_detected'] += 1
                    self.metrics['frames_with_face'] += 1
                    
                    # Calculate attention score
                    attention_score = self.calculate_attention_score(faces, frame.shape)
                    self.metrics['attention_scores'].append(attention_score)
                    
                    # Store face position
                    face_pos = {
                        'timestamp': time.time() - self.metrics['start_time'],
                        'position': faces[0].tolist(),
                        'attention_score': attention_score
                    }
                    self.metrics['face_position_history'].append(face_pos)
                    
                    # Draw on frame
                    self.draw_face_box(frame, faces, attention_score)
                    
                    # Show face count
                    cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                else:
                    self.metrics['frames_without_face'] += 1
                    cv2.putText(frame, "No Face Detected!", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Show timer
                elapsed = time.time() - self.metrics['start_time']
                remaining = max(0, duration_seconds - elapsed)
                timer_text = f"Time: {int(remaining)}s remaining"
                cv2.putText(frame, timer_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Engagement Tracker - CareerIntelli AI', frame)
            
            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n🛑 Tracking stopped by user")
                break
            
            # Check if duration completed
            if time.time() - self.metrics['start_time'] >= duration_seconds:
                print("\n✅ Tracking duration completed")
                break
            
            frame_count += 1
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Calculate final metrics
        self._calculate_final_metrics()
        
        return self.metrics
    
    def _calculate_final_metrics(self):
        """
        Calculate final metrics after tracking completes
        """
        self.metrics['end_time'] = time.time()
        self.metrics['session_duration'] = self.metrics['end_time'] - self.metrics['start_time']
        
        # Calculate average engagement score
        if self.metrics['attention_scores']:
            self.metrics['engagement_score'] = np.mean(self.metrics['attention_scores'])
        
        # Calculate attention percentage
        total_frames = self.metrics['total_frames']
        if total_frames > 0:
            self.metrics['attention_percentage'] = (self.metrics['frames_with_face'] / total_frames) * 100
        
        # Calculate face present/absent duration
        if self.metrics['session_duration'] > 0 and total_frames > 0:
            self.metrics['face_present_duration'] = (self.metrics['frames_with_face'] / total_frames) * self.metrics['session_duration']
            self.metrics['face_absent_duration'] = self.metrics['session_duration'] - self.metrics['face_present_duration']
    
    def analyze_pattern(self):
        """
        Analyze engagement patterns
        """
        if not self.metrics['attention_scores']:
            return {
                'pattern': 'No data available',
                'recommendation': 'Complete an engagement tracking session first'
            }
        
        scores = self.metrics['attention_scores']
        
        # Calculate trend
        if len(scores) > 1:
            first_half = np.mean(scores[:len(scores)//2])
            second_half = np.mean(scores[len(scores)//2:])
            
            if second_half > first_half + 10:
                trend = "Improving engagement"
            elif first_half > second_half + 10:
                trend = "Declining engagement - take break recommended"
            else:
                trend = "Consistent engagement"
        else:
            trend = "Insufficient data"
        
        # Generate recommendations
        avg_score = np.mean(scores)
        if avg_score < 50:
            recommendation = "Need to improve focus on camera. Practice maintaining eye contact."
        elif avg_score < 70:
            recommendation = "Good engagement but can improve. Try to stay centered in frame."
        else:
            recommendation = "Excellent engagement! Keep it up!"
        
        return {
            'pattern': trend,
            'average_engagement': round(np.mean(scores), 2),
            'max_engagement': round(np.max(scores), 2),
            'min_engagement': round(np.min(scores), 2),
            'recommendation': recommendation
        }
    
    def generate_report(self):
        """
        Generate detailed engagement report
        """
        pattern = self.analyze_pattern()
        
        report = {
            'session_summary': {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration_seconds': round(self.metrics['session_duration'], 2),
                'duration_formatted': time.strftime('%H:%M:%S', time.gmtime(self.metrics['session_duration']))
            },
            'engagement_metrics': {
                'overall_engagement_score': round(self.metrics['engagement_score'], 2),
                'attention_percentage': round(self.metrics['attention_percentage'], 2),
                'face_present_duration': round(self.metrics['face_present_duration'], 2),
                'face_absent_duration': round(self.metrics['face_absent_duration'], 2)
            },
            'frame_analysis': {
                'total_frames': self.metrics['total_frames'],
                'frames_with_face': self.metrics['frames_with_face'],
                'frames_without_face': self.metrics['frames_without_face'],
                'face_detection_rate': round(
                    (self.metrics['frames_with_face'] / self.metrics['total_frames'] * 100), 2
                ) if self.metrics['total_frames'] > 0 else 0
            },
            'pattern_analysis': pattern
        }
        
        # Add rating
        score = report['engagement_metrics']['overall_engagement_score']
        if score >= 80:
            report['rating'] = '🌟 Excellent'
        elif score >= 60:
            report['rating'] = '👍 Good'
        elif score >= 40:
            report['rating'] = '👌 Average'
        else:
            report['rating'] = '⚠️ Needs Improvement'
        
        return report
    
    def save_report(self, filename=None):
        """
        Save engagement report to file
        """
        if filename is None:
            filename = f"engagement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to: {filepath}")
        return filepath
    
    def get_engagement_score(self):
        """
        Return engagement score (for Talent Scorer)
        """
        return {
            'engagement_score': round(self.metrics.get('engagement_score', 0), 2),
            'attention_percentage': round(self.metrics.get('attention_percentage', 0), 2),
            'face_detection_rate': round(
                (self.metrics.get('frames_with_face', 0) / 
                 max(self.metrics.get('total_frames', 1), 1) * 100), 2
            ),
            'session_duration': round(self.metrics.get('session_duration', 0), 2)
        }
    
    def test_camera(self):
        """
        Test if camera is working
        """
        cap = cv2.VideoCapture(self.config['camera_id'])
        
        if not cap.isOpened():
            print("❌ Camera not available")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print("✅ Camera is working!")
            return True
        else:
            print("❌ Camera not responding")
            return False


# ------------------ TEST THE CODE ------------------
if __name__ == "__main__":
    print("=" * 60)
    print("ENGAGEMENT TRACKER TEST")
    print("=" * 60)
    
    # 1. Create tracker
    tracker = EngagementTracker()
    
    # 2. Test camera
    print("\n📸 Testing camera...")
    if tracker.test_camera():
        # 3. Quick test (10 seconds)
        print("\n🎯 Starting 10-second test tracking...")
        metrics = tracker.start_tracking(duration_seconds=10)
        
        if metrics:
            # 4. Print results
            print("\n📊 Tracking Results:")
            print(f"   Session duration: {metrics['session_duration']:.1f} seconds")
            print(f"   Engagement score: {metrics['engagement_score']:.1f}%")
            print(f"   Attention percentage: {metrics['attention_percentage']:.1f}%")
            
            # 5. Generate report
            report = tracker.generate_report()
            print(f"\n📋 Rating: {report['rating']}")
            print(f"   Recommendation: {report['pattern_analysis']['recommendation']}")
            
            # 6. Save report
            tracker.save_report()
    
    print("\n✨ Test complete!")