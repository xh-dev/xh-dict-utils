from xh_dual_layer_app_engine.Layer1AppEngine import AppEngine

from xh_dict_utils.command.LoadFile import LoadFile
from xh_dict_utils.command.LoadPipe import LoadPipe
from xh_dict_utils.command.Output import Output
from xh_dict_utils.command.Query import Query
from xh_dict_utils.command.RemoveNode import RemoveNode
from xh_dict_utils.command.ToArray import *
from xh_dict_utils.command.UpsertNode import UpsertNode


def main():
    PROGRAM_NAME = "yaml-json-modification"
    DESCRIPTION = "A simple program modify yaml or json file"
    appEngine = AppEngine(
        program_name=PROGRAM_NAME,
        description=DESCRIPTION,
    )

    appEngine.regSubCommandWithTemplate(LoadPipe())

    appEngine.regSubCommandWithTemplate(LoadFile())

    appEngine.regSubCommandWithTemplate(UpsertNode())

    appEngine.regSubCommandWithTemplate(RemoveNode())

    appEngine.regSubCommandWithTemplate(Query())

    appEngine.regSubCommandWithTemplate(ToArray())


    appEngine.regSubCommandWithTemplate(Output())

    appEngine.process(sys.argv)
