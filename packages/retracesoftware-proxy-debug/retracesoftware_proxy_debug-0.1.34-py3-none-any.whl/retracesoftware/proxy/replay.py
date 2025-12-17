import retracesoftware.functional as functional
import retracesoftware_utils as utils
import retracesoftware.stream as stream

from retracesoftware.install.tracer import Tracer
from retracesoftware.proxy.thread import per_thread_messages, thread_id
from retracesoftware.proxy.proxytype import *
# from retracesoftware.proxy.gateway import gateway_pair
from retracesoftware.proxy.record import StubRef
from retracesoftware.proxy.proxysystem import ProxySystem, RetraceError
from retracesoftware.proxy.stubfactory import StubFactory, Stub
from retracesoftware.proxy.globalref import GlobalRef

import os
import weakref
import traceback
import pprint
import inspect
import importlib
import itertools
from typing import Optional
import ast
import gc
from abc import ABC, abstractmethod

from itertools import count, islice

# we can have a dummy method descriptor, its has a __name__ and when called, returns the next element

# for types, we can patch the __new__ method
# do it from C and immutable types can be patched too
# patch the tp_new pointer?

class ReplayError(RetraceError):
    pass

def count_matching(*lists):
    count = 0
    for slice in zip(*lists):
        if len(set(slice)) == 1:
            count += 1
        else:
            break

    return count

def on_stack_mismatch(last_matching, record, replay):
    # print('Common:')
    # for index, common, replay, record in zip(count(), last_matching_stack, args[0], record):
    #     if common == replay == record:
    #         print(common)
    if last_matching:
        matching = count_matching(reversed(last_matching),
                                reversed(record),
                                reversed(replay))

        print('Common stacktrace:')
        for line in reversed(list(islice(reversed(last_matching), matching))):
            print(line)
        
        print('last matching stacktrace:')
        for line in islice(last_matching, 0, len(last_matching) - matching):
            print(line)

        print('Replay stacktrace:')
        for line in islice(replay, 0, len(replay) - matching):
            print(line)

        print('Record stacktrace:')
        for line in islice(record, 0, len(record) - matching):
            print(line)
        
        print(f'-----------')
    else:
        matching = count_matching(reversed(record), reversed(replay))

        print('Common stacktrace:')
        for line in reversed(list(islice(reversed(record), matching))):
            print(line)
        
        print('Replay stacktrace:')
        for line in islice(replay, 0, len(replay) - matching):
            print(line)

        print('Record stacktrace:')
        for line in islice(record, 0, len(record) - matching):
            print(line)
        
def frozen_to_module(name: str):
    """
    Given a frozen filename like "<frozen importlib._bootstrap>",
    return the actual module object (or None if not frozen).
    """
    if not name.startswith("<frozen ") or not name.endswith(">"):
        return None

    # Extract the part between <frozen ...>
    module_name = name[len("<frozen "):-1]

    # Special case: the stdlib ships some as _frozen_importlib and _frozen_importlib_external
    if module_name == "importlib._bootstrap":
        return sys.modules.get("_frozen_importlib") or importlib._bootstrap
    if module_name == "importlib._bootstrap_external":
        return sys.modules.get("_frozen_importlib_external") or importlib._bootstrap_external

    # Everything else is directly importable
    return importlib.import_module(module_name)

def get_function_at_line(filename: str, source: str, lineno: int) -> Optional[str]:
    """
    Return the name of the function (or class/method) that contains the given line number.
    
    Returns None if:
      - file not found
      - syntax error
      - line is outside any function (module level)
    """
    # except FileNotFoundError:
    #     return None
    # except UnicodeDecodeError:
    #     return None

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError:
        return None

    class FunctionFinder(ast.NodeVisitor):
        def __init__(self, target_lineno: int):
            self.target_lineno = target_lineno
            self.current: Optional[str] = None
            self.stack: list[str] = []

        def visit_FunctionDef(self, node):
            if node.lineno <= self.target_lineno <= node.end_lineno:
                # breakpoint()
                self.stack.append(node.name)
                self.current = node.name
                self.generic_visit(node)
                self.stack.pop()
            elif self.stack:
                # We're inside a nested function/class, keep traversing
                self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)  # same logic

        def visit_ClassDef(self, node):
            if node.lineno <= self.target_lineno <= node.end_lineno:
                self.stack.append(node.name)
                # Don't set current here — we prefer method names
                self.generic_visit(node)
                self.stack.pop()

        # def get_result(self) -> Optional[str]:
        #     if not self.stack:
        #         return None
        #     # Return the deepest (most specific) function/method name
        #     return self.current
        #     # return self.stack[-1]

    finder = FunctionFinder(lineno)
    finder.visit(tree)
    # print(f'foind: {finder.current}')
    return finder.current

def get_source(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return inspect.getsource(frozen_to_module(filename))

def all_elements_same(t):
    return len(set(t)) <= 1

def first(coll): return coll[0]

def common_prefix(*colls):
    return list(map(first, itertools.takewhile(all_elements_same, zip(*colls))))

def render_stack(frames):
    for filename,lineno in frames:
        try:
            source = get_source(filename)
            print(f'File "{filename}", line {lineno}, in {get_function_at_line(filename, source, lineno)}')
            print(f'  {source.splitlines()[lineno - 1].lstrip()}')
        except Exception:
            print(f'File not found: "{filename}", line {lineno}')

excludes = set([('/install/retracesoftware/proxy/replay.py', 210),
                ('/install/retracesoftware/proxy/replay.py', 175),
                ('/install/retracesoftware/stream.py', 176),
                ('/install/retracesoftware/stream.py', 179)])

def on_stack_difference(previous, record, replay):

    previous = [x for x in previous if x not in excludes]
    record = [x for x in record if x not in excludes]
    replay = [x for x in replay if x not in excludes]

    if record != replay:
        common = common_prefix(previous, record, replay) if previous else common_prefix(record, replay)
        
        if common:
            print('Common root:')
            render_stack(common)

        if previous:
            print('\nlast matching:')
            render_stack(previous[len(common):])

        print('\nrecord:')
        render_stack(record[len(common):])

        print('\nreplay:')
        render_stack(replay[len(common):])

        breakpoint()
        print(f'on_stack_difference!!!!!')

# def next_result_function(on_call, messages):
#     read_and_throw_error = functional.use_with(utils.raise_exception, messages, messages)

#     dispatch = {'CALL': on_call, 'RESULT': messages, 'ERROR': read_and_throw_error }

#     return functional.repeatedly(
#             functional.sequence(messages, dispatch.get, functional.apply))

class CallMessage:
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        try:
            self.func(*self.args, **self.kwargs)
        except BaseException:
            pass
        return None

class ResultMessage:
    def __init__(self, result):
        self.result = result

class ErrorMessage:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __call__(self):
        utils.raise_exception(self.type, self.value)

class CollectionMessage:
    def __init__(self, generation):
        self.generation = generation
    
    def __call__(self):
        gc.collect(self.generation)

def message_stream(source):
    dispatch = {
        'CALL': functional.use_with(CallMessage, source, source, source),
        'RESULT': functional.use_with(ResultMessage, source),
        'ERROR': functional.use_with(ErrorMessage, source, source),
        'ON_START_COLLECT': functional.use_with(CollectionMessage, source)
    }

    get_or_key = functional.use_with(dispatch.get, functional.identity, functional.constantly)

    # n = functional.if_then_else(
    #     dispatch.contains, 
    #     functional.sequence(dispatch.get, functional.apply),functional.identity)
    
    # def next(key): return dispatch[key]() if key in dispatch else key
            
    return functional.repeatedly(functional.sequence(source, get_or_key, functional.apply))

class ReplayProxySystem(ProxySystem):
    
    def after_fork_in_child(self):
        self.reader.path = self.new_child_path(self.reader.path)
        super().after_fork_in_child()

    # def dynamic_ext_proxytype(self, cls):
    #     raise Exception('dynamic_ext_proxytype should not be called in replay')

    @property
    def ext_apply(self): 
        return functional.repeatedly(self.next_result)

    def handle_async(self):
        while True:
            message = self.messages()

            if isinstance(message, CallMessage):
                message()
            elif isinstance(message, CollectionMessage):
                message()
                self.read_required('ON_END_COLLECT')
            elif self.skip_weakref_callbacks and message == 'ON_WEAKREF_CALLBACK_START':
                while message != 'ON_WEAKREF_CALLBACK_END':
                    message = self.messages()
            else:
                return message

    @utils.striptraceback
    def next_result(self):

        while True:
            message = self.handle_async()

            if isinstance(message, ResultMessage):
                return message.result
            elif isinstance(message, ErrorMessage):
                message()
            else:
                utils.sigtrap(message)

    def proxy__new__(self, __new__, *args, **kwargs):
        func = functional.repeatedly(self.next_result)
        func.__name__ = '__new__'
        return super().proxy__new__(func, *args, **kwargs)

    def basetype(self, cls):
        return self.stub_factory.create_stubtype(StubRef(cls))

    def do_collect(self):
        generation = self.messages()

        print(f'in do_collect!!!! {generation}')

        gc.collect(generation)

        self.read_required('ON_END_COLLECT')

    def mismatch(self, record, replay):
        try:
            utils.sigtrap([record, replay])
            print('---------------------------------')
            print('last matching stack')
            print('---------------------------------')
            if self.last_matching_stack:
                for line in self.last_matching_stack:
                    print(line)

            print('---------------------------------')
            print(f'Replay: {replay}')
            print('---------------------------------')
            for line in utils.stacktrace():
                print(line)
            print('---------------------------------')
            print(f'Record: {record}')
            print('---------------------------------')
            for i in range(15):
                print(self.messages())

            breakpoint()
            os._exit(1)
            raise Exception(f'Expected: {replay} but got: {record}')
        except:
            traceback.print_exc()
            utils.sigtrap('BAD!!!!')
            os._exit(1)

    def read_required(self, required):
        message = self.handle_async()

        if message != required:
            self.mismatch(record = message, replay = required)

    def trace_writer(self, name, *args):
        with self.thread_state.select('disabled'):
            # read = self.messages_read

            self.read_required('TRACE')
            # self.read_required(read)
            self.read_required(name)

            if name == 'stacktrace':
                print('FOOO!!!')
                os._exit(1)
                record = self.readnext()
                if args[0] == record:
                    self.last_matching_stack = args[0]
                else:
                    on_stack_mismatch(
                        last_matching = self.last_matching_stack,
                        record = record,
                        replay = args[0])
                    os._exit(1)
            else:
                # print(f'Trace: {self.reader.messages_read} {name} {args}')
                for arg in args:
                    self.read_required(arg)

    def on_thread_exit(self, thread_id):
        # print(f'on_thread_exit!!!!')
        self.reader.wake_pending()

    # def is_entry_frame(self, frame):
    #     if super().is_entry_frame(frame):
    #         filename = os.path.basename(frame.function.__code__.co_filename)
    #         scriptname = os.path.basename(self.mainscript)

    #         return filename == scriptname
    #     return False

    # def proxy_value(self, obj):
    #     utils.sigtrap('proxy_value')
        
    #     proxytype = dynamic_proxytype(handler = self.ext_dispatch, cls = type(obj))
    #     proxytype.__retrace_source__ = 'external'

    #     if self.on_proxytype: self.on_proxytype(proxytype)

    #     return utils.create_wrapped(proxytype, obj)

    # def on_new_ext_patched(self, obj):
    #     read = self.messages()
        
    #     # print(f'FOO: {read} {type(read)}')
    #     # assert isinstance(read, Placeholder)

    #     self.bindings[read] = obj

    def exclude_from_stacktrace(self, func):
        self.reader.exclude_from_stacktrace(func)

    # def skip_weakref_callback(self, callback):
    #     pass
    #     # return utils.observer(
    #     #     on_call = self.on_weakref_callback_start,
    #     #     on_result = self.on_weakref_callback_end,
    #     #     on_error = self.on_weakref_callback_end,
    #     #     function = callback)

    def __init__(self, 
                 reader,
                 thread_state,
                 immutable_types,
                 tracing_config,
                 tracecalls = None,
                 fork_path = [],
                 skip_weakref_callbacks = False):
        
        self.reader = reader
        self.skip_weakref_callbacks = skip_weakref_callbacks

        excludes = [ReplayProxySystem.checkpoint,
                    ReplayProxySystem.read_required,
                    ReplayProxySystem.trace_writer,
                    ReplayProxySystem.handle_async,
                    ReplayProxySystem.next_result.__wrapped__]
        
        for exclude in excludes:
            self.exclude_from_stacktrace(exclude)

        self.fork_path = fork_path

        self.messages = message_stream(thread_state.wrap('disabled', self.reader))

        self.stub_factory = StubFactory(thread_state = thread_state, next_result = self.next_result)

        self.last_matching_stack = None

        self.reader.type_deserializer[StubRef] = self.stub_factory
        self.reader.type_deserializer[GlobalRef] = lambda ref: ref()
                
        read_sync = thread_state.dispatch(utils.noop, internal = functional.lazy(thread_state.wrap('disabled', self.read_required), 'SYNC'))

        self.on_ext_call = functional.lazy(self.read_required, 'SYNC')

        self.sync = lambda function: utils.observer(on_call = read_sync, function = function)

        self.bind = self.reader.bind
        self.create_from_external = utils.noop

        if skip_weakref_callbacks:
            self.wrap_weakref_callback = \
                lambda callback: \
                    thread_state.dispatch(
                        callback, internal = self.disable_for(callback))
        else:
            self.on_weakref_callback_start = functional.lazy(self.read_required, 'ON_WEAKREF_CALLBACK_START')
            self.on_weakref_callback_end = functional.lazy(self.read_required, 'ON_WEAKREF_CALLBACK_END')

        super().__init__(thread_state = thread_state, 
                         tracer = Tracer(tracing_config, writer = self.trace_writer),
                         immutable_types = immutable_types,
                         tracecalls = tracecalls)

    def checkpoint(self, obj):
        self.read_required('CHECKPOINT')
        self.read_required(obj)

    def write_trace(self, obj):
        if 'TRACER' != self.messages():
            utils.sigtrap(obj)

        # self.read_required('TRACER')
        self.read_required(obj)
