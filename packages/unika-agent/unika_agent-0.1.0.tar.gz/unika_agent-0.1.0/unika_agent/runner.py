from unika_core import load_data, APP_NAME

def run_agent():
    data = load_data()
    return f"{APP_NAME} - Agent running with data: {data}"
