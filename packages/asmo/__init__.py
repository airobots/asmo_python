#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from . import configuration
from .controller import LocalController, WebController
from .attention import LocalAttention, WebAttention
from .memory import LocalMemory, WebMemory
from .process import LocalReflexProcess, WebReflexProcess, LocalNonReflexProcess, WebNonReflexProcess

is_running_local = configuration.is_running_local
set_local_run = controller.set_local_run
set_web_run = controller.set_web_run