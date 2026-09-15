class XGBoostModel:
    def __init__(self):
        self.is_trained = False
        
    def predict(self, window_features):
        return "WALKING", 0.95 # Stub label and confidence
