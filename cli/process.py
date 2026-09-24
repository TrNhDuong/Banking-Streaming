import subprocess

def run(args, input_text=None):
    print("$ " + " ".join(args), flush=True)
    return subprocess.run(args, input=input_text, text=True, check=True)
