from setuptools import setup, find_packages

setup(
    name="augmentations",
    package_dir={"": "src"},  # Указываем где искать пакеты
    packages=find_packages(where="src"),
)