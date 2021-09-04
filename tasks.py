from invoke import task
import os
import shutil


@task
def clean(c):
    def dir_walk(path: str):
        for entry in os.scandir(path):
            if entry.name == "__pycache__":
                shutil.rmtree(entry.path)
            elif entry.is_dir():
                dir_walk(entry.path)

    dir_walk(os.path.abspath("src"))

@task
def run(c):
    import pymop
    pymop.main()
    clean(c)
