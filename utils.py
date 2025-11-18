import pandas as pd
from io import BytesIO

def import_tasks_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    tasks = df.to_dict(orient="records")
    return tasks

def export_tasks_to_excel(tasks):
    df = pd.DataFrame(tasks)
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    return output
