from setuptools import setup, find_packages

HYPEN_E_DOT="-e ."
def get_requirements(file_path:str)->list:
    """
    This function will return the list of requirements
    """
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n", "") for req in requirements]
        
        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
            
    return requirements


setup(
    name="ML Project",
    version= "0.0.1",
    author="Suman",
    author_email = "mr.sarkar4478987656@gmail.com",
    packages=find_packages(),
    install_requires= get_requirements("requirements.txt")
)