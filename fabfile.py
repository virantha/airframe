from fabric.api import *
import os
 
  
def build_windows_dist():
    if os.name == 'nt':
        # Call the pyinstaller
        local("python ../pyinstaller/pyinstaller.py airframe_windows.spec --onefile")


def run_tests():
    test_dir = "test"
    with lcd(test_dir):
        # Regenerate the test script
        local("py.test --genscript=runtests.py")
        t = local("py.test --cov-config .coveragerc --cov=airframe --cov-report=term --cov-report=html", capture=False)

        #with open("test/COVERAGE.rst", "w") as f:
            #f.write(t)


def push_docs():
    """ Build the sphinx docs from develop
        And push it to gh-pages
    """
    githubpages = "/Users/virantha/dev/githubdocs/airframe"
    with lcd(githubpages):
        local("git checkout gh-pages")
        local("git pull origin gh-pages")
    with lcd("docs"):
        print("Running sphinx in docs/ and building to ~/dev/githubpages/airframe")
        local("make clean")
        local("make html")
        local("cp -R ../test/htmlcov %s/html/testing" % githubpages)
    with lcd(githubpages):
        local("git add .")
        local('git commit -am "doc update"')
        local('git push origin gh-pages')

