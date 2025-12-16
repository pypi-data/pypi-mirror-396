# -*- coding: utf-8 -*-
# datastore.py

import filecmp
import getpass
import tempfile
import warnings
from pathlib import Path

from pybis import Openbis


class DataStore:
    url = None
    token = None
    _availObj = None
    _userspace = None

    def __init__(self, url, username=None, tokenValidTo=None):
        self.url = url
        self.username = username
        if self.username is None:
            self.username = getpass.getuser()
        print(f"Working as user '{self.username}'.")
        # to generate PAT you need to login normally
        self.ds = Openbis(url=self.url, verify_certificates=True)
        # arg. *save_token* saves the openBIS token to ~/.pybis permanently
        self.ds.login(
            self.username,
            getpass.getpass(prompt=f"Password for {self.username}: "),
            save_token=False,
        )
        # create the PAT with the given name, don't store it
        self.token = self.ds.get_or_create_personal_access_token(
            "test-session", validTo=tokenValidTo
        )

    @property
    def userspace(self):
        uspace = self._userspace
        if uspace is None:
            allspaces = self.ds.get_spaces()
            uspace = allspaces.df[
                allspaces.df.code.str.endswith(self.username.upper())
            ].code.values[0]
            self._userspace = uspace
        return uspace

    @userspace.setter
    def userspace(self, name):
        name = name.upper()
        if name in self.ds.get_spaces().df.code.values:
            self._userspace = name

    @staticmethod
    def identifier(objects, code):
        return objects[objects.code == code].identifier.tolist()[0]

    def createProject(self, projectName, space, spacePrefix=None):
        """Finds the requested project in the DataStore.
        Matching project names can be limited to a given *spacePrefix*.
        If the project is not found, a new project with the given code in the given space
        is created."""
        # get available projects, accessible by the current user
        projectsAvail = self.ds.get_projects()
        if spacePrefix:
            projectsAvail = [prj for prj in projectsAvail if f"/{spacePrefix}_" in prj.identifier]
        projects = [prj for prj in projectsAvail if prj.code == projectName]
        assert len(projects) <= 1, f"Multiple projects found for '{projectName}'"
        dsProject = None
        if len(projects):  # get the existing object
            dsProject = projects[0]
        else:  # create it, if not found
            print(f"Creating project '{projectName}'")
            dsProject = self.ds.new_project(code=projectName, space=space)
            dsProject.save()
        assert dsProject
        return dsProject

    def createCollection(self, collName, projectObj, defaultObjType=None):
        collections = self.ds.get_collections(project=projectObj)
        dsColl = [coll for coll in collections if coll.code == collName.upper()]
        if len(dsColl):
            dsColl = dsColl[0]
        else:  # create it, if not found
            print(f"Creating collection '{collName}'")
            dsColl = self.ds.new_collection(
                code=collName, type="COLLECTION", project=projectObj, props={"$name": collName}
            )
            dsColl.save()
        assert dsColl
        # update properties (name, default view and object type) if not set)
        props = dsColl.props.all()  # props as dict
        propKey = "$name"
        if propKey in props and props[propKey] is None:
            props[propKey] = collName
        propKey = "$default_collection_view"
        if propKey in props.keys() and props[propKey] is None:
            propVal = [
                item
                for item in self.ds.get_vocabulary(propKey + "s").get_terms().df.code
                if "list" in item.lower()
            ]
            assert len(propVal)
            props[propKey] = propVal[0]
        if defaultObjType:
            propKey = "$default_object_type"
            if propKey in props.keys() and props[propKey] is None:
                props[propKey] = defaultObjType
        # print(f"Setting '{collName}' properties:\n  {props}")
        dsColl.set_props(props)
        dsColl.save()
        return dsColl

    def createObject(
        self,
        projectName: str,
        collectionName: str = None,
        space: str = None,
        spacePrefix: str = None,
        objType: str = None,
        props: dict = None,
    ):
        dsProject = self.createProject(projectName, space, spacePrefix=spacePrefix)
        dsColl = None
        if collectionName is None:  # collectionName is required
            return None
        dsColl = self.createCollection(collectionName, dsProject, defaultObjType=objType)
        obj = self.ds.get_objects(type=objType, where={"$name": props["$name"]}).objects
        if len(obj):
            obj = obj[0]
            prefix = objType
            msg = "'{}' exists already in {}! Updating ...".format(
                obj.props["$name"], obj.project.identifier
            )
            warnings.warn_explicit(msg, UserWarning, prefix, 0)
        else:  # does not exist yet
            objName = f" '{props['$name']}'" if len(props.get("$name", "")) else ""
            print(f"Creating new {objType}{objName} in {dsColl.identifier}")
            obj = self.ds.new_object(type=objType, props=props, collection=dsColl)
        obj.set_props(props)
        return obj

    def findObjects(self, *args, **kwargs):
        return self.ds.get_objects(**kwargs)

    def uploadDataset(self, obj, datasetType, fpaths=[]):
        def _checkFile(localPath, remoteFiles):
            remoteFile = [f for f in remoteFiles if f.name == localPath.name]
            if not len(remoteFile):  # file exists in the dataset as well
                return False
            return filecmp.cmp(localPath, remoteFile[0], shallow=False)

        if not len(fpaths):
            return  # nothing to do
        for dataset in obj.get_datasets(type=datasetType):
            with tempfile.TemporaryDirectory() as tempdir:
                dataset.download(destination=tempdir)
                dsFiles = [f for f in Path(tempdir).rglob("*") if f.is_file()]
                if len(fpaths) == len(dsFiles):
                    if all([_checkFile(fpath, dsFiles) for fpath in fpaths]):
                        print(
                            f"All local files of {datasetType} match files in dataset, "
                            "not updating."
                        )
                        continue  # skip deletion below
            print(f"Dataset {datasetType} needs update, deleting existing dataset:")
            dataset.delete("Needs update")
        if not len(obj.get_datasets(type=datasetType)):  # didn't exist yet or all deleted
            dataset = self.ds.new_dataset(
                type=datasetType, collection=obj.collection, object=obj, files=fpaths
            )
            dataset.save()
