import os
from django.conf import settings
import joblib
import numpy as np

BASE_DIR = settings.BASE_DIR

priority_model = joblib.load(os.path.join(BASE_DIR, 'ml_models/priority_model.pkl'))
resolution_model = joblib.load(os.path.join(BASE_DIR, 'ml_models/resolution_model.pkl'))

le_category = joblib.load(os.path.join(BASE_DIR, 'ml_models/le_category.pkl'))
le_area = joblib.load(os.path.join(BASE_DIR, 'ml_models/le_area.pkl'))
le_severity = joblib.load(os.path.join(BASE_DIR, 'ml_models/le_severity.pkl'))
# le_department = joblib.load(os.path.join(BASE_DIR, 'ml_models/le_department.pkl'))
le_priority = joblib.load(os.path.join(BASE_DIR, 'ml_models/le_priority.pkl'))


def predict(category, area, severity, affected_people, month, day_of_week, is_weekend):

    # Encode
    category = le_category.transform([category])[0]
    area = le_area.transform([area])[0]
    severity = le_severity.transform([severity])[0]
    # department = le_department.transform([department])[0]

    priority_input = np.array([[category, area, severity, affected_people, month, day_of_week, is_weekend]])
    resolution_input = np.array([[category,area,severity,affected_people]])

    # Predict
    priority = priority_model.predict(priority_input)[0]
    days = resolution_model.predict(resolution_input)[0]

    # Decode
    priority = le_priority.inverse_transform([priority])[0]

    return priority, round(days, 2)