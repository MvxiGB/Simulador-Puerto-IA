import numpy as np
from sklearn.ensemble import RandomForestRegressor

CARGO_DATABASE = {
    1: ("Contenedores", "TEUs"),
    2: ("Granel", "Toneladas"),
    3: ("Vehículos", "Unidades"),
    4: ("Carga Peligrosa", "Pallets")
}

class CongestionPredictor:
    """Classic ML model (Random Forest) to predict PURE loading times based on cargo and weather."""
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self._train_dummy_model()

    def _train_dummy_model(self):
        """Trains the model with mock historical port cargo data focusing on weather."""
        X_train = np.array([
            [1, 1, 20], [2, 2, 150], [4, 4, 40],
            [1, 3, 10], [5, 1, 35], [2, 2, 80]
        ])
        y_train = np.array([12.0, 30.0, 50.0, 18.0, 45.0, 22.0])
        self.model.fit(X_train, y_train)

    def predict_load_time(self, weather: int, cargo_code: int, qty: int) -> float:
        """Predicts exact pure loading time mathematically."""
        return self.model.predict(np.array([[weather, cargo_code, qty]]))[0]