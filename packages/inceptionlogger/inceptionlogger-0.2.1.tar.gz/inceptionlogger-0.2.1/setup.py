import os
from setuptools import setup, find_packages, Command

package_folder = os.path.dirname(__file__)
env_file_path = os.path.join(package_folder, ".env")


class CleanUpCommand(Command):
    """Custom command to remove files created by inceptionlogger."""

    description = "Clean up files created by inceptionlogger"
    user_options = []

    def initialize_options(self):
        # create the .env file
        with open(env_file_path, "w") as f:
            f.write(f'facility="setup"')

    def finalize_options(self):
        pass

    def run(self):

        if os.path.exists(env_file_path):
            print(f"Removing file: {env_file_path}")
            os.remove(env_file_path)
        else:
            print(f"No .env file found in {package_folder}.")

        print("Cleanup complete.")


setup(
    name="inceptionlogger",
    version="0.2.1",
    author="KhaduaBloom",
    author_email="khaduabloom@gmail.com",
    description="inceptionlogger is a package that allows you to log your application to graylog",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KhaduaBloom/inceptionforcepackages/tree/main/PythonPackage/inceptionLogger",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13.0",
    install_requires=[
        "graypy==2.1.0",
        "psutil==6.1.0",
        "fastapi",
        "uvicorn",
        "pydantic-settings",
    ],
    cmdclass={
        "cleanup": CleanUpCommand,
    },
)
