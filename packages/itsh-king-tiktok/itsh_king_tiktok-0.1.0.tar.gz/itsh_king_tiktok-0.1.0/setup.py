from setuptools import setup, find_packages

setup(
    name="itsh_king_tiktok",
    version="0.1.0",
    description="Simple Python library",
    packages=find_packages(),
    install_requires=["requests"],  # ← بين علامات اقتباس
    python_requires=">=3.7",
)
