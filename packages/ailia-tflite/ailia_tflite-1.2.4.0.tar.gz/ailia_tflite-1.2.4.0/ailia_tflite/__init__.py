import ctypes
import os
import sys
import platform

import numpy

#### dependency check
if sys.platform == "win32":
    import ctypes
    try:
        for library in ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"]:
            ctypes.windll.LoadLibrary(library)
    except:
        print("  WARNING Please install MSVC 2015-2019 runtime from https://docs.microsoft.com/ja-jp/cpp/windows/latest-supported-vc-redist")
    is_imx8mp = False
else:
    is_imx8mp = 'nodename' in os.uname().__dir__() and 'imx8mp' in os.uname().nodename
    if is_imx8mp:
        import tflite_runtime.interpreter as tflite_runtime_interpreter

#### load dll
if sys.platform == "win32" :
    dll_platform = "windows/x64"
    dll_name = "ailia_tflite.dll"
    mkl_name = "libiomp5md.dll"
    load_fn = ctypes.WinDLL
elif sys.platform == "darwin" :
    dll_platform = "mac"
    dll_name = "libailia_tflite.dylib"
    mkl_name = "libiomp5.dylib"
    load_fn = ctypes.CDLL
else :
    is_arm = "arm" in platform.machine() or platform.machine() == "aarch64"
    if is_arm:
        if platform.architecture()[0] == "32bit":
            dll_platform = "linux/armeabi-v7a"
        else:
            dll_platform = "linux/arm64-v8a"
    else:
        dll_platform = "linux/x64"
    dll_name = "libailia_tflite.so"
    mkl_name = "libiomp5.so"
    load_fn = ctypes.CDLL

dll_found = False
candidate = ["", str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep), str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep) + dll_platform + str(os.sep)]

for dir in candidate :
    try :
        mkl_dll = load_fn(dir + mkl_name)   # preload dependent mkl library
    except :
        pass

for dir in candidate :
    try :
        dll = load_fn(dir + dll_name)
        dll_found = True
    except :
        pass
if (not dll_found) and (not is_imx8mp) :
    msg = "DLL load failed : \'" + dll_name + "\' is not found"
    raise ImportError(msg)

from .license import *

# ==============================================================================
# generated from ailia_tflite.h
from ctypes import *

AILIA_TFLITE_TENSOR_TYPE_FLOAT32 = ( 0 )
AILIA_TFLITE_TENSOR_TYPE_FLOAT16 = ( 1 )
AILIA_TFLITE_TENSOR_TYPE_INT32 = ( 2 )
AILIA_TFLITE_TENSOR_TYPE_UINT8 = ( 3 )
AILIA_TFLITE_TENSOR_TYPE_INT64 = ( 4 )
AILIA_TFLITE_TENSOR_TYPE_STRING = ( 5 )
AILIA_TFLITE_TENSOR_TYPE_BOOL = ( 6 )
AILIA_TFLITE_TENSOR_TYPE_INT16 = ( 7 )
AILIA_TFLITE_TENSOR_TYPE_COMPLEX64 = ( 8 )
AILIA_TFLITE_TENSOR_TYPE_INT8 = ( 9 )
AILIA_TFLITE_STATUS_SUCCESS = ( 0 )
AILIA_TFLITE_STATUS_INVALID_ARGUMENT = ( - 1 )
AILIA_TFLITE_STATUS_OUT_OF_RANGE = ( - 2 )
AILIA_TFLITE_STATUS_MEMORY_INSUFFICIENT = ( - 3 )
AILIA_TFLITE_STATUS_BROKEN_MODEL = ( - 4 )
AILIA_TFLITE_STATUS_INVALID_PARAMETER = ( - 5 )
AILIA_TFLITE_STATUS_PARAMETER_NOT_FOUND = ( - 6 )
AILIA_TFLITE_STATUS_UNSUPPORTED_OPCODE = ( - 7 )
AILIA_TFLITE_STATUS_LICENSE_NOT_FOUND = ( - 8 )
AILIA_TFLITE_STATUS_LICENSE_BROKEN = ( - 9 )
AILIA_TFLITE_STATUS_LICENSE_EXPIRED = (- 10 )
AILIA_TFLITE_STATUS_INVALID_STATE = (- 11 )
AILIA_TFLITE_STATUS_OTHER_ERROR = ( - 128 )

AILIATFLiteInstance = c_void_p

AILIA_TFLITE_ENV_REFERENCE = 0
AILIA_TFLITE_ENV_NNAPI = 1
AILIA_TFLITE_ENV_MMALIB = 2
AILIA_TFLITE_ENV_MMALIB_COMPATIBLE = 3
AILIA_TFLITE_ENV_MAX = 4

AILIA_TFLITE_MEMORY_MODE_DEFAULT = 0
AILIA_TFLITE_MEMORY_MODE_REDUCE_INTERSTAGE = 1
AILIA_TFLITE_MEMORY_MODE_MAX = 2

AILIA_TFLITE_CPU_FEATURES_NONE = 0
AILIA_TFLITE_CPU_FEATURES_NEON = 1
AILIA_TFLITE_CPU_FEATURES_SSE2 = 2
AILIA_TFLITE_CPU_FEATURES_SSE4_2 = 4
AILIA_TFLITE_CPU_FEATURES_AVX = 8
AILIA_TFLITE_CPU_FEATURES_AVX2 = 16
AILIA_TFLITE_CPU_FEATURES_VNNI = 32
AILIA_TFLITE_CPU_FEATURES_AVX512 = 64

AILIA_TFLITE_FLAG_NONE = 0
AILIA_TFLITE_FLAG_INPUT_AND_OUTPUT_TENSORS_USE_SCRATCH = 1

AILIA_TFLITE_PROFILE_MODE_DISABLE = 0
AILIA_TFLITE_PROFILE_MODE_ENABLE = 1
AILIA_TFLITE_PROFILE_MODE_TRACE = 2
AILIA_TFLITE_PROFILE_MODE_MEMORY = 4

AILIA_TFLITE_SCRATCH_INT_SIZE_DEFAULT = 261948
AILIA_TFLITE_SCRATCH_MID_SIZE_DEFAULT = 1816576
AILIA_TFLITE_SCRATCH_EXT_SIZE_DEFAULT = 104857600

class ailia_tflite:
    def __init__(self):
        self.lib = dll # modified
        self.lib.ailiaTFLiteCreate.restype = c_int
        self.lib.ailiaTFLiteCreate.argtypes = (POINTER(c_void_p), c_void_p, c_size_t, c_void_p, c_void_p, c_void_p, c_void_p, c_int32, c_int32, c_int32, ) # modified

        self.lib.ailiaTFLiteDestroy.restype = None
        self.lib.ailiaTFLiteDestroy.argtypes = (c_void_p, )

        self.lib.ailiaTFLiteAllocateTensors.restype = c_int
        self.lib.ailiaTFLiteAllocateTensors.argtypes = (c_void_p, )

        self.lib.ailiaTFLiteResizeInputTensor.restype = c_int
        self.lib.ailiaTFLiteResizeInputTensor.argtypes = (c_void_p, c_int, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetNumberOfInputs.restype = c_int
        self.lib.ailiaTFLiteGetNumberOfInputs.argtypes = (c_void_p, POINTER(c_int), )

        self.lib.ailiaTFLiteGetInputTensorIndex.restype = c_int
        self.lib.ailiaTFLiteGetInputTensorIndex.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetNumberOfOutputs.restype = c_int
        self.lib.ailiaTFLiteGetNumberOfOutputs.argtypes = (c_void_p, POINTER(c_int), )

        self.lib.ailiaTFLiteGetOutputTensorIndex.restype = c_int
        self.lib.ailiaTFLiteGetOutputTensorIndex.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetTensorDimension.restype = c_int
        self.lib.ailiaTFLiteGetTensorDimension.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetTensorShape.restype = c_int
        self.lib.ailiaTFLiteGetTensorShape.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetTensorShapeSignature.restype = c_int
        self.lib.ailiaTFLiteGetTensorShapeSignature.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetTensorType.restype = c_int
        self.lib.ailiaTFLiteGetTensorType.argtypes = (c_void_p, c_char_p, c_int, )

        self.lib.ailiaTFLiteGetTensorBuffer.restype = c_int
        self.lib.ailiaTFLiteGetTensorBuffer.argtypes = (c_void_p, POINTER(c_void_p), c_int, )

        self.lib.ailiaTFLiteGetTensorName.restype = c_int
        self.lib.ailiaTFLiteGetTensorName.argtypes = (c_void_p, POINTER(c_char_p), c_int, )

        self.lib.ailiaTFLiteGetTensorQuantizationCount.restype = c_int
        self.lib.ailiaTFLiteGetTensorQuantizationCount.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetTensorQuantizationScale.restype = c_int
        self.lib.ailiaTFLiteGetTensorQuantizationScale.argtypes = (c_void_p, POINTER(c_float), c_int, )

        self.lib.ailiaTFLiteGetTensorQuantizationZeroPoint.restype = c_int
        self.lib.ailiaTFLiteGetTensorQuantizationZeroPoint.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetTensorQuantizationQuantizedDimension.restype = c_int
        self.lib.ailiaTFLiteGetTensorQuantizationQuantizedDimension.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLitePredict.restype = c_int
        self.lib.ailiaTFLitePredict.argtypes = (c_void_p, )

        self.lib.ailiaTFLiteGetNodeCount.restype = c_int
        self.lib.ailiaTFLiteGetNodeCount.argtypes = (c_void_p, POINTER(c_int), )

        self.lib.ailiaTFLiteGetNodeOperator.restype = c_int
        self.lib.ailiaTFLiteGetNodeOperator.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetNodeInputCount.restype = c_int
        self.lib.ailiaTFLiteGetNodeInputCount.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetNodeInputTensorIndex.restype = c_int
        self.lib.ailiaTFLiteGetNodeInputTensorIndex.argtypes = (c_void_p, POINTER(c_int), c_int, c_int, )

        self.lib.ailiaTFLiteGetNodeOutputCount.restype = c_int
        self.lib.ailiaTFLiteGetNodeOutputCount.argtypes = (c_void_p, POINTER(c_int), c_int, )

        self.lib.ailiaTFLiteGetNodeOutputTensorIndex.restype = c_int
        self.lib.ailiaTFLiteGetNodeOutputTensorIndex.argtypes = (c_void_p, POINTER(c_int), c_int, c_int, )

        self.lib.ailiaTFLiteGetNodeOption.restype = c_int
        self.lib.ailiaTFLiteGetNodeOption.argtypes = (c_void_p, c_void_p, c_int, c_char_p, )

        self.lib.ailiaTFLiteGetOperatorName.restype = c_int
        self.lib.ailiaTFLiteGetOperatorName.argtypes = (POINTER(c_char_p), c_int, )

        self.lib.ailiaTFLiteSetProfileMode.restype = c_int
        self.lib.ailiaTFLiteSetProfileMode.argtypes = (c_void_p, c_int, )

        self.lib.ailiaTFLiteGetSummaryLength.restype = c_int
        self.lib.ailiaTFLiteGetSummaryLength.argtypes = (c_void_p, POINTER(c_size_t), )

        self.lib.ailiaTFLiteGetSummary.restype = c_int
        self.lib.ailiaTFLiteGetSummary.argtypes = (c_void_p, c_char_p, c_size_t, )

        self.lib.ailiaTFLiteGetErrorDetail.restype = c_int
        self.lib.ailiaTFLiteGetErrorDetail.argtypes = (c_void_p, POINTER(c_char_p) )

        self.lib.ailiaTFLiteGetCpuFeatures.restype = c_int
        self.lib.ailiaTFLiteGetCpuFeatures.argtypes = (c_void_p, POINTER(c_int), )

        self.lib.ailiaTFLiteSetCpuFeatures.restype = c_int
        self.lib.ailiaTFLiteSetCpuFeatures.argtypes = (c_void_p, c_int, )

        self.lib.ailiaTFLiteGetVersion.restype = ctypes.c_char_p
        self.lib.ailiaTFLiteGetVersion.argtypes = None

        self.lib.ailiaTFLiteSetScratchBuffer.restype = c_int
        self.lib.ailiaTFLiteSetScratchBuffer.argtypes = (c_void_p, c_void_p, c_size_t, c_void_p, c_size_t, c_void_p, c_size_t)

    def Create(self, arg0, arg1, arg2, arg3, arg4, arg5): # modified
        return self.lib.ailiaTFLiteCreate(cast(pointer(arg0), POINTER(c_void_p)), cast(pointer(arg1), c_void_p), arg2, None, None, None, None, arg3, arg4, arg5) # modified
    def Destroy(self, arg0):
        return self.lib.ailiaTFLiteDestroy(cast(arg0, c_void_p)) # modified
    def AllocateTensors(self, arg0):
        return self.lib.ailiaTFLiteAllocateTensors(cast(arg0, c_void_p)) # modified
    def ResizeInputTensor(self, arg0, arg1, arg2, arg3):
        return self.lib.ailiaTFLiteResizeInputTensor(cast(arg0, c_void_p), arg1, cast(pointer(arg2), POINTER(c_int)), arg3) # modified
    def GetNumberOfInputs(self, arg0, arg1):
        return self.lib.ailiaTFLiteGetNumberOfInputs(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int))) # modified
    def GetInputTensorIndex(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetInputTensorIndex(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def GetNumberOfOutputs(self, arg0, arg1):
        return self.lib.ailiaTFLiteGetNumberOfOutputs(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int))) # modified
    def GetOutputTensorIndex(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetOutputTensorIndex(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def GetTensorDimension(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorDimension(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def GetTensorShape(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorShape(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def GetTensorShapeSignature(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorShapeSignature(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def GetTensorType(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorType(cast(arg0, c_void_p), cast(pointer(arg1), c_char_p), arg2) # modified
    def GetTensorBuffer(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorBuffer(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_void_p)), arg2) # modified
    def GetTensorName(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorName(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_char_p)), arg2) # modified
    def GetTensorQuantizationCount(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorQuantizationCount(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def GetTensorQuantizationScale(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorQuantizationScale(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_float)), arg2) # modified
    def GetTensorQuantizationZeroPoint(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorQuantizationZeroPoint(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def GetTensorQuantizationQuantizedDimension(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetTensorQuantizationQuantizedDimension(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2) # modified
    def Predict(self, arg0):
        return self.lib.ailiaTFLitePredict(cast(arg0, c_void_p)) # modified
    def GetNodeCount(self, arg0, arg1):
        return self.lib.ailiaTFLiteGetNodeCount(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)))
    def GetNodeOperator(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetNodeOperator(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2)
    def GetNodeInputCount(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetNodeInputCount(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2)
    def GetNodeInputTensorIndex(self, arg0, arg1, arg2, arg3):
        return self.lib.ailiaTFLiteGetNodeInputTensorIndex(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2, arg3)
    def GetNodeOutputCount(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetNodeOutputCount(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2)
    def GetNodeOutputTensorIndex(self, arg0, arg1, arg2, arg3):
        return self.lib.ailiaTFLiteGetNodeOutputTensorIndex(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)), arg2, arg3)
    def GetNodeOption(self, arg0, arg1, arg2, arg3):
        return self.lib.ailiaTFLiteGetNodeOption(cast(arg0, c_void_p), pointer(arg1), arg2, arg3)
    def GetOperatorName(self, arg0, arg1):
        return self.lib.ailiaTFLiteGetOperatorName(cast(pointer(arg0), POINTER(c_char_p)), arg1)
    def SetProfileMode(self, arg0, arg1):
        return self.lib.ailiaTFLiteSetProfileMode(cast(arg0, c_void_p), c_int(arg1))
    def GetSummaryLength(self, arg0, arg1):
        return self.lib.ailiaTFLiteGetSummaryLength(cast(arg0, c_void_p), pointer(arg1))
    def GetSummary(self, arg0, arg1, arg2):
        return self.lib.ailiaTFLiteGetSummary(cast(arg0, c_void_p), arg1, arg2)
    def GetErrorDetail(self, arg0, arg1):
        return self.lib.ailiaTFLiteGetErrorDetail(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_char_p)))
    def GetCpuFeatures(self, arg0, arg1):
        return self.lib.ailiaTFLiteGetCpuFeatures(cast(arg0, c_void_p), cast(pointer(arg1), POINTER(c_int)))
    def SetCpuFeatures(self, arg0, arg1):
        return self.lib.ailiaTFLiteSetCpuFeatures(cast(arg0, c_void_p), c_int(arg1))
    def GetVersion(self):
        return self.lib.ailiaTFLiteGetVersion().decode()
    def SetScratchBuffer(self, arg0, arg1, arg2, arg3, arg4, arg5, arg6):
        return self.lib.ailiaTFLiteSetScratchBuffer(cast(arg0, c_void_p), cast(pointer(arg1), c_void_p), arg2, cast(pointer(arg3), c_void_p), arg4, cast(pointer(arg5), c_void_p), arg6)

# ==============================================================================


class AiliaTFLiteError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(f"{message} code:{code}")
        self.code = code

class Interpreter:
    """
    | ailia TFLite Runtime inference interface (compatible with tf.lite.interpreter)
    | ailia TFLite Runtime 推論用インターフェース(tf.lite.Interpreterと互換)
    """
    def __init__(self, model_path = None, env_id : int = AILIA_TFLITE_ENV_REFERENCE, memory_mode : int = AILIA_TFLITE_MEMORY_MODE_DEFAULT, flags : int = AILIA_TFLITE_FLAG_NONE,
                 scratch_int_size : int = AILIA_TFLITE_SCRATCH_INT_SIZE_DEFAULT, scratch_mid_size : int = AILIA_TFLITE_SCRATCH_MID_SIZE_DEFAULT, scratch_ext_size : int = AILIA_TFLITE_SCRATCH_EXT_SIZE_DEFAULT,
                 **kwargs):
        """
        | Constructor
        | コンストラクタ

        Parameters
        ----------
        model_path : str
            | Path to tflite model
            | tfliteモデルへのパス
        env_id : int
            | Used when using NNAPI in Android ID in the execution environment
            | 実行環境のID、AndroidでNNAPIを使用する場合に使用
        memory_mode : int
            | ailia_tflite.AILIA_TFLITE_MEMORY_REDUCE_INTERSTAGE can be used by specifying the memory mode.
            | ailia_tflite.AILIA_TFLITE_MEMORY_MODE_REDUCE_INTERSTAGEを指定することで省メモリモードが使用可能
        flags : int
            | You can change the reasoning mode by specifying ailia_tflite.AILIA_TFLITE_FLAG_*
            | ailia_tflite.AILIA_TFLITE_FLAG_*を指定することで推論モードを変更可能
        """
        self.instance = None
        if model_path is None:
            raise ValueError("ailia tflite runtime must provide model_path")
        tflite_file = open(model_path, 'rb')
        tflite_data = tflite_file.read()
        self.tflite_cdata = (ctypes.c_byte * len(tflite_data))()
        input_ptr = numpy.array(tflite_data).ctypes.data_as(POINTER(ctypes.c_int8))
        ctypes.memmove(self.tflite_cdata, input_ptr, len(tflite_data) * ctypes.sizeof(ctypes.c_int8))
        self.tflite_clength = ctypes.c_size_t(len(tflite_data))
        self.dll = ailia_tflite()
        if not("perpetual_license" in self.dll.GetVersion()):
            check_and_download_license()
        self.instance = AILIATFLiteInstance()
        self.__check(self.dll.Create(self.instance, self.tflite_cdata, self.tflite_clength, ctypes.c_int32(env_id), ctypes.c_int32(memory_mode), flags))
        if env_id == AILIA_TFLITE_ENV_MMALIB or env_id == AILIA_TFLITE_ENV_MMALIB_COMPATIBLE:
            self.scratch_int = (ctypes.c_byte * scratch_int_size)()
            self.scratch_int_size = ctypes.c_size_t(len(self.scratch_int))
            self.scratch_mid = (ctypes.c_byte * scratch_mid_size)()
            self.scratch_mid_size = ctypes.c_size_t(len(self.scratch_mid))
            self.scratch_ext = (ctypes.c_byte * scratch_ext_size)()
            self.scratch_ext_size = ctypes.c_size_t(len(self.scratch_ext))
            self.__check(self.dll.SetScratchBuffer(self.instance, self.scratch_int, self.scratch_int_size, self.scratch_mid, self.scratch_mid_size, self.scratch_ext, self.scratch_ext_size))


    def __del__(self):
        if self.instance:
            self.dll.Destroy(self.instance)

    def __check(self, status):
        if status != AILIA_TFLITE_STATUS_SUCCESS:
            detail = ""
            if status == AILIA_TFLITE_STATUS_LICENSE_NOT_FOUND:
                detail = "(License not found)"
            elif status == AILIA_TFLITE_STATUS_LICENSE_EXPIRED:
                detail = "(License expired)"
            else:
                detail_p = c_char_p()
                self.dll.GetErrorDetail(self.instance, detail_p)
                if detail_p.value is not None:
                    detail = "("+detail_p.value.decode('utf-8')+")"
            raise AiliaTFLiteError(f"ailia tflite runtime error "+detail, status)

    def allocate_tensors(self):
        """
        | Allocate tensor buffers
        | Tensorの割当を行う
        """
        self.__check(self.dll.AllocateTensors(self.instance))

    def resize_tensor_input(self, tensor_index, shape, strict=False):
        """
        | Change input tensor shape
        | 入力Tensorの形状を変更する

        Parameters
        ----------
        tensor_index : int
            | Index of Tensor (index returned by Get_input_details)
            | Tensorのindex(get_input_detailsが返すindex)
        shape : Union[Tuple, nd.array, List]
            | New shape
            | 新しい形状
        strict : bool, optional
            | Strict mode. In the case of true, only unknown dimensions (parts that are -1 in Shape_Signature) can be changed. by default False
            | 厳格モード。Trueの場合不明な次元(shape_signatureで-1となっている部分)のみ変更可能です。デフォルトはFalseです。
        """
        input_details = self.get_input_details()
        input_index = -1
        for i in range(len(input_details)):
            if input_details[i]["index"] == tensor_index:
                input_index = i

        if input_index == -1:
            raise RuntimeError("cannot find input tensor")

        input_detail = input_details[input_index]
        dim = len(shape)
        if len(input_detail["shape"]) != dim:
            raise RuntimeError("new shape must be same dim")
        if strict:
            for i in range(dim):
                if shape[i] != input_detail["shape"][i] and input_detail["shape_signature"][i] != -1:
                    raise RuntimeError("cannot modify except unknown dimension")
        cshape = (ctypes.c_int32 * dim)()
        for i in range(dim):
            cshape[i] = shape[i]
        self.__check(self.dll.ResizeInputTensor(self.instance, input_index, cshape, dim))

    def __get_tensor(self, tensor_index):
        table_nptypes = [numpy.float32, numpy.float64, numpy.int32, numpy.uint8, numpy.int64, None, numpy.bool_, numpy.int16, numpy.complex64, numpy.int8]
        c_int_buf = ctypes.c_int32()
        detail = {}

        detail['index'] = tensor_index

        self.__check(self.dll.GetTensorDimension(self.instance, c_int_buf, tensor_index))
        dimension = c_int_buf.value

        cshape = (ctypes.c_int32 * dimension)()
        self.__check(self.dll.GetTensorShape(self.instance, cshape, tensor_index))
        detail['shape'] = numpy.array(cshape, dtype=numpy.int32)

        cshape_signature = (ctypes.c_int32 * dimension)()
        self.__check(self.dll.GetTensorShapeSignature(self.instance, cshape_signature, tensor_index))
        detail['shape_signature'] = numpy.array(cshape_signature, dtype=numpy.int32)

        self.__check(self.dll.GetTensorType(self.instance, c_int_buf, tensor_index))
        detail['dtype'] = table_nptypes[c_int_buf.value]

        name = c_char_p()
        self.__check(self.dll.GetTensorName(self.instance, name, tensor_index))
        detail['name'] = name.value.decode('utf-8')

        # quantize
        self.__check(self.dll.GetTensorQuantizationCount(self.instance, c_int_buf, tensor_index))
        quantized_count = c_int_buf.value
        if quantized_count > 0:
            self.__check(self.dll.GetTensorQuantizationQuantizedDimension(self.instance, c_int_buf, tensor_index))
            quantized_dimension = c_int_buf.value

            cscale = (ctypes.c_float * quantized_count)()
            self.__check(self.dll.GetTensorQuantizationScale(self.instance, cscale, tensor_index))

            czero_point = (ctypes.c_int64 * quantized_count)()
            self.__check(self.dll.GetTensorQuantizationZeroPoint(self.instance, czero_point, tensor_index))

            detail['quantization'] = (cscale[0], czero_point[0])
            detail['quantization_parameters'] = {
                "scales": numpy.array(cscale, dtype=numpy.float32),
                "zero_points": numpy.array(czero_point, dtype=numpy.int32),
                "quantized_dimension": quantized_dimension
            }
        return detail

    def get_input_details(self):
        """
        | Get information of input tensor
        | 入力Tensorの情報を取得する

        Returns
        -------
        List[Dict[str, any]]
            | Input tensor information array
            | 入力Tensorの情報の配列。

        References
        -------
        index
            | Tensor index
            | Tensorのindex
        shape
            | Tensor shape(numpy array)
            | Tensorの形状(numpy array)
        shape_signature
            | Tensor shape signature(numpy array) Unlike Shape, if the shape is undecided, -1 is stored.
            | Tensorの形状(numpy array) shapeと異なり、形状が未定な場合は-1が格納される。
        dtype
            | Tensor type
            | Tensorの型
        name
            | Tensor name
            | Tensor名
        quantization
            | Quantization information(deprecated)
            | 量子化情報(deprecated)
        quantization_parameters
            | Quantization parameters
            | 量子化情報
        quantization_parameters.scales
            | Array of scale (1 element when quantizing in tensor units)
            | スケールの配列 (Tensor単位で量子化する場合は1要素)
        quantization_parameters.zero_points
            | Array of zero point (1 element when quantizing in tensor units)
            | ゼロポイントの配列 (Tensor単位で量子化する場合は1要素)
        quantization_parameters.quantized_dimension
            | Axis of quantization (Specify when quantizing in axis units)
            | 量子化を行う軸 (axis単位で量子化する場合に指定)
        """
        input_details = []
        c_int_buf = ctypes.c_int32()
        self.__check(self.dll.GetNumberOfInputs(self.instance, c_int_buf))
        number_of_inputs = c_int_buf.value
        for i in range(number_of_inputs):
            input_detail = {}
            self.__check(self.dll.GetInputTensorIndex(self.instance, c_int_buf, i))
            input_details.append(self.__get_tensor(c_int_buf.value))
        return input_details

    def get_output_details(self):
        """
        | Get information of output tensor
        | 出力Tensorの情報を取得する

        Returns
        -------
        List[Dict[str, any]]
            | Output tensor information array
            | 出力Tensorの情報の配列

        References
        -------
        index
            | Tensor index
            | Tensorのindex
        shape
            | Tensor shape(numpy array)
            | Tensorの形状(numpy array)
        shape_signature
            | Tensor shape signature(numpy array) Unlike Shape, if the shape is undecided, -1 is stored.
            | Tensorの形状(numpy array) shapeと異なり、形状が未定な場合は-1が格納される。
        dtype
            | Tensor type
            | Tensorの型
        name
            | Tensor name
            | Tensor名
        quantization
            | Quantization information(deprecated)
            | 量子化情報(deprecated)
        quantization_parameters
            | Quantization parameters
            | 量子化情報
        quantization_parameters.scales
            | Array of scale (1 element when quantizing in tensor units)
            | スケールの配列 (Tensor単位で量子化する場合は1要素)
        quantization_parameters.zero_points
            | Array of zero point (1 element when quantizing in tensor units)
            | ゼロポイントの配列 (Tensor単位で量子化する場合は1要素)
        quantization_parameters.quantized_dimension
            | Axis of quantization (Specify when quantizing in axis units)
            | 量子化を行う軸 (axis単位で量子化する場合に指定)
        """
        output_details = []
        c_int_buf = ctypes.c_int32()
        self.__check(self.dll.GetNumberOfOutputs(self.instance, c_int_buf))
        number_of_outputs = c_int_buf.value
        for i in range(number_of_outputs):
            self.__check(self.dll.GetOutputTensorIndex(self.instance, c_int_buf, i))
            output_details.append(self.__get_tensor(c_int_buf.value))
        return output_details

    def set_tensor(self, tensor_index, value):
        """
        | Set the value in the specified tensor
        | 指定したTensorに値をセットする

        Parameters
        ----------
        tensor_index : int
            | TENSOR's index (acquired with get_input_details)
            | Tensorのindex(get_input_detailsで取得する)
        value : np.ndarray
            | The value to set
            | セットする値
        """
        c_int_buf = ctypes.c_int32()
        self.__check(self.dll.GetTensorDimension(self.instance, c_int_buf, tensor_index))
        dimension = c_int_buf.value
        cshape = (ctypes.c_int32 * dimension)()
        self.__check(self.dll.GetTensorShape(self.instance, cshape, tensor_index))
        length = 1
        for i in cshape:
            length *= i
        input_reshaped = numpy.reshape(value, length)
        c_buffer = ctypes.c_void_p()
        self.__check(self.dll.GetTensorBuffer(self.instance, c_buffer, tensor_index))
        self.__check(self.dll.GetTensorType(self.instance, c_int_buf, tensor_index))
        tensor_type = c_int_buf.value
        table_ctypes = [ctypes.c_float, ctypes.c_double, ctypes.c_int32, ctypes.c_uint8, ctypes.c_int64, None, ctypes.c_bool, ctypes.c_int16, None, ctypes.c_int8]
        table_nptypes = [numpy.float32, numpy.float64, numpy.int32, numpy.uint8, numpy.int64, None, numpy.bool_, numpy.int16, numpy.complex64, numpy.int8]
        input_ptr = input_reshaped.astype(dtype=table_nptypes[tensor_type]).ctypes.data_as(POINTER(table_ctypes[tensor_type]))
        ctypes.memmove(c_buffer, input_ptr, length * ctypes.sizeof(table_ctypes[tensor_type]))

    def get_tensor(self, tensor_index):
        """
        | Get the value of the specified tensor
        | 指定したTensorの値を取得する

        Parameters
        ----------
        tensor_index : int
            | Tensor's index (acquired with get_output_details)
            | Tensorのindex(get_output_detailsで取得する)

        Returns
        -------
        np.ndarray
            | Tensor value
            | Tensorの値
        """
        c_int_buf = ctypes.c_int32()
        self.__check(self.dll.GetTensorDimension(self.instance, c_int_buf, tensor_index))
        dimension = c_int_buf.value
        cshape = (ctypes.c_int32 * dimension)()
        self.__check(self.dll.GetTensorShape(self.instance, cshape, tensor_index))
        length = 1
        shape = ()
        for i in cshape:
            length *= i
            shape += (i,)
        table_ctypes = [ctypes.c_float, ctypes.c_double, ctypes.c_int32, ctypes.c_uint8, ctypes.c_int64, None, ctypes.c_bool, ctypes.c_int16, None, ctypes.c_int8]
        c_buffer = ctypes.c_void_p()
        self.__check(self.dll.GetTensorBuffer(self.instance, c_buffer, tensor_index))
        self.__check(self.dll.GetTensorType(self.instance, c_int_buf, tensor_index))
        tensor_type = c_int_buf.value
        coutput = ctypes.cast(c_buffer, ctypes.POINTER(table_ctypes[tensor_type]))

        table_nptypes = [numpy.float32, numpy.float64, numpy.int32, numpy.uint8, numpy.int64, None, numpy.bool_, numpy.int16, numpy.complex64, numpy.int8]
        return numpy.ctypeslib.as_array(coutput, shape=(length,)).copy().astype(dtype=table_nptypes[tensor_type]).reshape(shape)

    def invoke(self):
        """
        | Inference
        | 推論を実行する
        """
        self.__check(self.dll.Predict(self.instance))

    def get_node_infos(self):
        """
        | Get node information
        | Nodeの情報を取得する

        Returns
        -------
        List[Dict[str, any]]
            | Node information array
            | Nodeの情報の配列

        References
        -------
        index
            | Node index
            | Nodeのindex
        name
            | Node name
            | Nodeの名前
        operator
            | Operator enum value
            | Operatorのenum値
        operator_name
            | Operator name
            | Operatorの名前
        input_tensor_indices
            | List of index of input tensor
            | 入力TensorのindexのList
        input_details
            | List of information in input tensor
            | 入力Tensorの情報のList
        output_tensor_index
            | Index of output tensor
            | 出力Tensorのindex
        output_detail
            | Output tensor information
            | 出力Tensorの情報
        weight
            | Weight (for Conv2D/DepthwiseConv2D/Fullyconnected)
            | Weight (Conv2D/DepthwiseConv2D/FullyConnectedの場合)
        weight_detail
            | Weight detail (for Conv2D/DepthwiseConv2D/Fullyconnected)
            | Weightの情報 (Conv2D/DepthwiseConv2D/FullyConnectedの場合)
        bias
            | Bias (for Conv2D/DepthwiseConv2D/Fullyconnected)
            | Bias (Conv2D/DepthwiseConv2D/FullyConnectedの場合)
        bias_detail
            | Bias detail(for Conv2D/DepthwiseConv2D/Fullyconnected)
            | Biasの情報 (Conv2D/DepthwiseConv2D/FullyConnectedの場合)
        option
            | Dict of option name and value (for Add/Conv2D/DepthwiseConv2D/FullyConnected/MaxPool2D/Softmax/Mean)
            | オプション名と値のDict (Add/Conv2D/DepthwiseConv2D/FullyConnected/MaxPool2D/Softmax/Meanの場合)
        """
        details = []
        c_int_buf = ctypes.c_int32()
        self.__check(self.dll.GetNodeCount(self.instance, c_int_buf))
        nnode = c_int_buf.value
        for i in range(nnode):
            detail = {}
            detail['index'] = i
            self.__check(self.dll.GetNodeOperator(self.instance, c_int_buf, i))
            op = c_int_buf.value
            detail['operator'] = op
            op_name = c_char_p()
            self.__check(self.dll.GetOperatorName(op_name, op))
            detail['operator_name'] = op_name.value.decode('utf-8')
            details.append(detail)
            self.__check(self.dll.GetNodeInputCount(self.instance, c_int_buf, i))
            input_tensor_indices = []
            ninput = c_int_buf.value
            for j in range(ninput):
                self.__check(self.dll.GetNodeInputTensorIndex(self.instance, c_int_buf, i, j))
                input_tensor_indices.append(c_int_buf.value)
            detail['input_tensor_indices'] = input_tensor_indices
            input_details = []
            for j in input_tensor_indices:
                input_details.append(self.__get_tensor(j))
            detail['input_details'] = input_details
            self.__check(self.dll.GetNodeOutputTensorIndex(self.instance, c_int_buf, i, 0))
            output_tensor_index = c_int_buf.value
            detail['output_tensor_index'] = output_tensor_index
            output_detail = self.__get_tensor(output_tensor_index)
            detail['output_detail'] = output_detail
            detail['name'] = output_detail['name']
            def append_weight(input_index):
                tensor_index = input_tensor_indices[input_index]
                detail['weight'] = self.get_tensor(tensor_index)
                detail['weight_detail'] = self.__get_tensor(tensor_index)
            def append_bias(input_index):
                tensor_index = input_tensor_indices[input_index]
                detail['bias'] = self.get_tensor(tensor_index)
                detail['bias_detail'] = self.__get_tensor(tensor_index)
            if op == 0: # Add
                option = {}
                c_i8_option_value_buf = ctypes.c_int8()
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"fused_activation_function")
                option['fused_activation_function'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"pot_scale_int16")
                option['pot_scale_int16'] = c_i8_option_value_buf.value
                detail['option'] = option
            elif op == 3: # Conv2D
                append_weight(1)
                append_bias(2)
                option = {}
                c_i8_option_value_buf = ctypes.c_int8()
                c_i32_option_value_buf = ctypes.c_int32()
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"padding")
                option['padding'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"stride_w")
                option['stride_w'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"stride_h")
                option['stride_h'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"fused_activation_function")
                option['fused_activation_function'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"dilation_w_factor")
                option['dilation_w_factor'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"dilation_h_factor")
                option['dilation_h_factor'] = c_i32_option_value_buf.value
                detail['option'] = option
            elif op == 4: # DepthwiseConv2D
                append_weight(1)
                append_bias(2)
                option = {}
                c_i8_option_value_buf = ctypes.c_int8()
                c_i32_option_value_buf = ctypes.c_int32()
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"padding")
                option['padding'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"stride_w")
                option['stride_w'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"stride_h")
                option['stride_h'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"depth_multiplier")
                option['depth_multiplier'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"fused_activation_function")
                option['fused_activation_function'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"dilation_w_factor")
                option['dilation_w_factor'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"dilation_h_factor")
                option['dilation_h_factor'] = c_i32_option_value_buf.value
                detail['option'] = option
            elif op == 9: # FullyConnected
                append_weight(1)
                append_bias(2)
                option = {}
                c_i8_option_value_buf = ctypes.c_int8()
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"fused_activation_function")
                option['fused_activation_function'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"weights_format")
                option['weights_format'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"keep_num_dims")
                option['keep_num_dims'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"asymmetric_quantize_inputs")
                option['asymmetric_quantize_inputs'] = c_i8_option_value_buf.value
                detail['option'] = option
            elif op == 17: # MaxPool2D
                option = {}
                c_i8_option_value_buf = ctypes.c_int8()
                c_i32_option_value_buf = ctypes.c_int32()
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"padding")
                option['padding'] = c_i8_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"stride_w")
                option['stride_w'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"stride_h")
                option['stride_h'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"filter_width")
                option['filter_width'] = c_i32_option_value_buf.value
                self.dll.GetNodeOption(self.instance, c_i32_option_value_buf, i, b"filter_height")
                option['filter_height'] = c_i32_option_value_buf.value
                detail['option'] = option
            elif op == 25: # Softmax
                option = {}
                c_f32_option_value_buf = ctypes.c_float()
                self.dll.GetNodeOption(self.instance, c_f32_option_value_buf, i, b"beta")
                option['beta'] = c_f32_option_value_buf.value
                detail['option'] = option
            elif op == 40: # Mean
                option = {}
                c_i8_option_value_buf = ctypes.c_int8()
                self.dll.GetNodeOption(self.instance, c_i8_option_value_buf, i, b"keep_dims")
                option['keep_dims'] = c_i8_option_value_buf.value
                detail['option'] = option
        return details

    def set_profile_mode(self, profile_mode):
        """
        | Enable profile mode
        | プロファイルモードを指定する

        | It must be executed immediately after creation of an interpreter. After setting the profile mode, you can get profile information by calling get_summary.
        | Interpreterの作成直後に実行する必要がある。プロファイルモードを設定した後にget_summaryを呼び出すことで、プロファイル情報を取得可能。

        Parameters
        ----------
        profile_mode : bool or int
            | Profile mode (enabled in true)
            | プロファイルモード（Trueで有効）
        """
        if profile_mode == False:
            profile_mode = AILIA_TFLITE_PROFILE_MODE_DISABLE
        if profile_mode == True:
            profile_mode = AILIA_TFLITE_PROFILE_MODE_ENABLE
        self.__check(self.dll.SetProfileMode(self.instance, profile_mode))

    def get_summary(self):
        """
        | Get the summary information
        | サマリを取得する

        Returns
        -------
        str
            | Summary information
            | サマリ情報
        """
        buffer_size = c_size_t()
        self.__check(self.dll.GetSummaryLength(self.instance, buffer_size))
        buffer = create_string_buffer(buffer_size.value)
        self.__check(self.dll.GetSummary(self.instance, buffer, buffer_size))
        return buffer.value.decode('utf-8')

    def get_cpu_features(self):
        """
        | Get the CPU instrunction to use
        | 使用するCPU命令を取得する

        Returns
        -------
        int
            | AILIA_TFLITE_CPU_FEATURES_XXX logical sum
            | AILIA_TFLITE_CPU_FEATURES_XXXの論理和
        """
        details = []
        c_int_buf = ctypes.c_int32()
        self.__check(self.dll.GetCpuFeatures(self.instance, c_int_buf))
        return c_int_buf.value

    def set_cpu_features(self, cpu_features):
        """
        | Set the CPU instruction to use
        | 使用するCPU命令を設定する

        Parameters
        ----------
        cpu_features : int
            | AILIA_TFLITE_CPU_FEATURES_XXX logical sum
            | AILIA_TFLITE_CPU_FEATURES_XXXの論理和
        """
        self.__check(self.dll.SetCpuFeatures(self.instance, cpu_features))


# ==============================================================================
class ailia_tflite_delegate(ailia_tflite):
    def __init__(self):
        self.tflite_interpreter = None
        vx_delegate = tflite_runtime_interpreter.load_delegate(library='/usr/lib/libvx_delegate.so')
        self.experimental_delegates = [vx_delegate]
        self._clear_details()

    def _clear_details(self):
        self.tensor_details = None
        self.input_details = None
        self.output_details = None
    def _get_tensor_details(self):
        if self.tensor_details is None:
            self.tensor_details = self.tflite_interpreter.get_tensor_details()
        return self.tensor_details
    def _get_input_details(self):
        if self.input_details is None:
            self.input_details = self.tflite_interpreter.get_input_details()
        return self.input_details
    def _get_output_details(self):
        if self.output_details is None:
            self.output_details = self.tflite_interpreter.get_output_details()
        return self.output_details

    def SetExperimentalDelegates(self, experimental_delegates):
        self.experimental_delegates = experimental_delegates
    def SetTfliteInterpreterTensor(self, tensor_index, value):
        self.tflite_interpreter.set_tensor(tensor_index, value)
    def GetTfliteInterpreterTensor(self, tensor_index):
        return self.tflite_interpreter.get_tensor(tensor_index)

    def CreateFromFile(self, model_path):
        ret = AILIA_TFLITE_STATUS_SUCCESS
        try:
            self.tflite_interpreter = tflite_runtime_interpreter.Interpreter(model_path=model_path, experimental_delegates=self.experimental_delegates)
        except:
            ret = AILIA_TFLITE_STATUS_OTHER_ERROR
        if self.tflite_interpreter is None:
            ret = AILIA_TFLITE_STATUS_OTHER_ERROR
        return ret

    def Create(self, arg0, arg1, arg2, arg3, arg4, arg5):
        self._clear_details()
        temp_model_filename = '.tmp.tflite'
        buf = c_char * int(arg2.value)
        buf = buf.from_address(int(cast(pointer(arg1), c_void_p).value))
        with open(temp_model_filename, 'wb') as f:
            f.write(buf)
        return self.CreateFromFile(temp_model_filename)
    def Destroy(self, arg0):
        return AILIA_TFLITE_STATUS_SUCCESS
    def AllocateTensors(self, arg0):
        self.tflite_interpreter.allocate_tensors()
        return AILIA_TFLITE_STATUS_SUCCESS
    def ResizeInputTensor(self, arg0, arg1, arg2, arg3):
        self._clear_details()
        shape = c_int * int(arg3)
        shape = shape.from_address(int(cast(pointer(arg2), c_void_p).value))
        self.tflite_interpreter.resize_tensor_input(int(arg1), shape)
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetNumberOfInputs(self, arg0, arg1):
        input_details = self._get_input_details()
        arg1.value = len(input_details)
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetInputTensorIndex(self, arg0, arg1, arg2):
        input_details = self._get_input_details()
        arg1.value = input_details[int(arg2)]['index']
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetNumberOfOutputs(self, arg0, arg1):
        output_details = self._get_output_details()
        arg1.value = len(output_details)
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetOutputTensorIndex(self, arg0, arg1, arg2):
        output_details = self._get_output_details()
        arg1.value = output_details[int(arg2)]['index']
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorDimension(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        arg1.value = len(tensor_details[int(arg2)]['shape'])
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorShape(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        for i in range(len(arg1)):
            arg1[i] = tensor_details[int(arg2)]['shape'][i]
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorShapeSignature(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        for i in range(len(arg1)):
            arg1[i] = tensor_details[int(arg2)]['shape_signature'][i]
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorType(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        dtype = tensor_details[int(arg2)]['dtype']
        atype = AILIA_TFLITE_TENSOR_TYPE_UINT8
        if dtype == numpy.uint8:
            atype = AILIA_TFLITE_TENSOR_TYPE_UINT8
        elif dtype == numpy.int8:
            atype = AILIA_TFLITE_TENSOR_TYPE_INT8
        elif dtype == numpy.float32:
            atype = AILIA_TFLITE_TENSOR_TYPE_FLOAT32
        elif dtype == numpy.float16:
            atype = AILIA_TFLITE_TENSOR_TYPE_FLOAT16
        elif dtype == numpy.int32:
            atype = AILIA_TFLITE_TENSOR_TYPE_INT32
        elif dtype == numpy.int64:
            atype = AILIA_TFLITE_TENSOR_TYPE_INT64
        arg1.value = atype
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorBuffer(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        shape = tensor_details[int(arg2)]['shape']
        dtype = tensor_details[int(arg2)]['dtype']
        ctype = numpy.ctypeslib.as_ctypes_type(dtype)
        dimension = 1
        for s in shape:
            dimension *= s
        buffer = (ctype * dimension)()
        arg1.value = cast(buffer, c_void_p).value
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorName(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        arg1.value = tensor_details[int(arg2)]['name'].encode('utf-8')
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorQuantizationCount(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        arg1.value = len(tensor_details[int(arg2)]['quantization_parameters']['scales'])
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorQuantizationScale(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        for i in range(len(arg1)):
            arg1[i] = tensor_details[int(arg2)]['quantization_parameters']['scales'][i]
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorQuantizationZeroPoint(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        for i in range(len(arg1)):
            arg1[i] = tensor_details[int(arg2)]['quantization_parameters']['zero_points'][i]
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetTensorQuantizationQuantizedDimension(self, arg0, arg1, arg2):
        tensor_details = self._get_tensor_details()
        value = tensor_details[int(arg2)].get('quantized_dimension', None)
        if value is not None and arg1.value is not None:
            arg1.value = value
        return AILIA_TFLITE_STATUS_SUCCESS
    def Predict(self, arg0):
        try:
            self.tflite_interpreter.invoke()
        except:
            return AILIA_TFLITE_STATUS_OTHER_ERROR
        return AILIA_TFLITE_STATUS_SUCCESS
    def GetNodeCount(self, arg0, arg1):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetNodeOperator(self, arg0, arg1, arg2):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetNodeInputCount(self, arg0, arg1, arg2):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetNodeInputTensorIndex(self, arg0, arg1, arg2, arg3):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetNodeOutputCount(self, arg0, arg1, arg2):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetNodeOutputTensorIndex(self, arg0, arg1, arg2, arg3):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetNodeOption(self, arg0, arg1, arg2, arg3):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetOperatorName(self, arg0, arg1):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def SetProfileMode(self, arg0, arg1):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetSummaryLength(self, arg0, arg1):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetSummary(self, arg0, arg1, arg2):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetErrorDetail(self, arg0, arg1):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def GetCpuFeatures(self, arg0, arg1):
        return AILIA_TFLITE_STATUS_OTHER_ERROR
    def SetCpuFeatures(self, arg0, arg1):
        return AILIA_TFLITE_STATUS_OTHER_ERROR

if is_imx8mp:
    ailia_tflite = ailia_tflite_delegate

class Interpreter_delegate(Interpreter):
    def __init__(self, model_path = None, env_id : int = AILIA_TFLITE_ENV_REFERENCE, memory_mode : int = AILIA_TFLITE_MEMORY_MODE_DEFAULT, flags : int = AILIA_TFLITE_FLAG_NONE, **kwargs):
        if model_path is None:
            raise ValueError("ailia tflite runtime must provide model_path")
        if len(kwargs) > 0:
            raise ValueError(f"ailia tflite runtime does not support argment ({kwargs.keys()[0]}) currently")
        self.dll = ailia_tflite_delegate()
        self.instance = AILIATFLiteInstance()
        status = self.dll.CreateFromFile(model_path)
        if status != AILIA_TFLITE_STATUS_SUCCESS:
            raise AiliaTFLiteError(f"ailia tflite runtime error", status)
    def set_tensor(self, tensor_index, value):
        self.dll.SetTfliteInterpreterTensor(tensor_index, value)
    def get_tensor(self, tensor_index):
        return self.dll.GetTfliteInterpreterTensor(tensor_index)

if is_imx8mp:
    Interpreter = Interpreter_delegate
