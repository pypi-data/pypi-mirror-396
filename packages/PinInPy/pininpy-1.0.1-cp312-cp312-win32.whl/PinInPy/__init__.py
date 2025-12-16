from ._pinin4cpp_cffi import lib,ffi
from enum import IntEnum
import cffi

_pffi = ffi

ffi = cffi.FFI()

__version__ = "1.0.1"
__all__ = ["PinIn", "TreeSearcher", "Logic", "Keyboard", "PinInConfig", "DeserializeException", "PinInInitException", "TreeSearcherInitException"]

def _create_pinin(handle):
    if handle == ffi.NULL:
        return None
    return ffi.gc(handle,lib.PinInCpp_PinIn_Free)
    
def _create_tree_searcher(handle):
    if handle == ffi.NULL:
        return None
    return ffi.gc(handle,lib.PinInCpp_TreeSearcher_Free)

class Logic(IntEnum):
    '''匹配逻辑，传递给TreeSearcher用的'''
    BEGIN = lib.PinInCpp_BEGIN
    '''前缀匹配：必须从字符串开头开始匹配'''
    CONTAIN = lib.PinInCpp_CONTAIN
    '''部分匹配：匹配字符串中的任意位置字串'''
    EQUAL = lib.PinInCpp_EQUAL
    '''完全匹配：字面意思'''

class Keyboard(IntEnum):
    '''不能自定义的预设键位枚举'''
    NULLKeyboard = lib.PinInCpp_NULLKeyboard
    '''代表不改变Keyboard，特殊的枚举量'''
    QUANPIN = lib.PinInCpp_QUANPIN
    '''基础的全拼方案 PinIn类的默认方案'''
    DAQIAN = lib.PinInCpp_DAQIAN
    '''注音（大千）输入法方案'''
    XIAOHE = lib.PinInCpp_XIAOHE
    '''小鹤双拼方案'''
    ZIRANMA = lib.PinInCpp_ZIRANMA
    '''自然码双拼方案'''
    SOUGOU = lib.PinInCpp_SOUGOU
    '''搜狗双拼方案'''
    ZHINENG_ABC = lib.PinInCpp_ZHINENG_ABC
    '''智能ABC双拼方案'''
    GUOBIAO = lib.PinInCpp_GUOBIAO
    '''国标双拼方案'''
    MICROSOFT = lib.PinInCpp_MICROSOFT
    '''微软双拼方案'''
    PINYINPP = lib.PinInCpp_PINYINPP
    '''拼音加加双拼方案'''
    ZIGUANG = lib.PinInCpp_ZIGUANG
    '''紫光双拼方案'''

class PinInConfig:
    '''配置PinIn的匹配逻辑，一定要调用commit方法，不然设置是不会生效的'''
    __pinin:PinIn
    '''PinInConfig所属的PinIn对象'''
    keyboard:Keyboard
    '''键位枚举'''
    fZh2Z:bool
    '''zh -> z模糊音'''
    fSh2S:bool
    '''sh -> s模糊音'''
    fCh2C:bool
    '''ch -> c模糊音'''
    fAng2An:bool
    '''ang -> an模糊音'''
    fIng2In:bool
    '''ing -> in模糊音'''
    fEng2En:bool
    '''eng -> en模糊音'''
    fU2V:bool
    '''u -> v模糊音'''
    fFirstChar:bool
    '''实际上是强制把首字母加入到匹配列表，但是全拼匹配有序列匹配的逻辑，所以实际上一定程度上有首字母匹配，但是开启这个可以把一些更加不严格的拼音搜索匹配到。比如：toding == 铜锭，只会在这个生效的时候有用'''
    def __init__(self, pinin:PinIn):
        self.__pinin = pinin
        rawCfg = lib.PinInCpp_PinIn_GetConfig(pinin.cdata)
        self.keyboard = rawCfg.keyboard
        self.fZh2Z = rawCfg.fZh2Z != bytes([0])
        self.fSh2S = rawCfg.fSh2S != bytes([0])
        self.fCh2C = rawCfg.fCh2C != bytes([0])
        self.fAng2An = rawCfg.fAng2An != bytes([0])
        self.fIng2In = rawCfg.fIng2In != bytes([0])
        self.fEng2En = rawCfg.fEng2En != bytes([0])
        self.fU2V = rawCfg.fU2V != bytes([0])
        self.fFirstChar = rawCfg.fFirstChar != bytes([0])
    def set_keyboard(self, keyboard:Keyboard):
        '''
        设置 keyboard 字段为输入参数
        '''
        self.keyboard = keyboard
        return self
    def set_fZh2Z(self, enable:bool):
        '''
        设置 fZh2Z 字段为输入参数
        '''
        self.fZh2Z = enable
        return self
    def set_fSh2S(self, enable:bool):
        '''
        设置 fSh2S 字段为输入参数
        '''
        self.fSh2S = enable
        return self
    def set_fCh2C(self, enable:bool):
        '''
        设置 fCh2C 字段为输入参数
        '''
        self.fCh2C = enable
        return self
    def set_fAng2An(self, enable:bool):
        '''
        设置 fAng2An 字段为输入参数
        '''
        self.fAng2An = enable
        return self
    def set_fIng2In(self, enable:bool):
        '''
        设置 fIng2In 字段为输入参数
        '''
        self.fIng2In = enable
        return self
    def set_fEng2En(self, enable:bool):
        '''
        设置 fEng2En 字段为输入参数
        '''
        self.fEng2En = enable
        return self
    def set_fU2V(self, enable:bool):
        '''
        设置 fU2V 字段为输入参数
        '''
        self.fU2V = enable
        return self
    def set_fFirstChar(self, enable:bool):
        '''
        设置 fFirstChar 字段为输入参数
        '''
        self.fFirstChar = enable
        return self

    def commit(self):
        '''
        提交所更改的配置以生效
        '''
        rawCfg = lib.PinInCpp_PinIn_GetConfig(self.__pinin.cdata)
        rawCfg.keyboard = self.keyboard
        rawCfg.fZh2Z = bytes([self.fZh2Z and 1 or 0])
        rawCfg.fSh2S = bytes([self.fSh2S and 1 or 0])
        rawCfg.fCh2C = bytes([self.fCh2C and 1 or 0])
        rawCfg.fAng2An = bytes([self.fAng2An and 1 or 0])
        rawCfg.fIng2In = bytes([self.fIng2In and 1 or 0])
        rawCfg.fEng2En = bytes([self.fEng2En and 1 or 0])
        rawCfg.fU2V = bytes([self.fU2V and 1 or 0])
        rawCfg.fFirstChar = bytes([self.fFirstChar and 1 or 0])
        lib.PinInCpp_PinIn_ConfigCommit(self.__pinin.cdata, rawCfg)
        pass

class DeserializeException(Exception):
    '''PinIn4Cpp反序列化时出现的错误'''
    message = "Normal?"
    code = "PinInCpp_DeserNormal"
    def __init__(self, code):
        if code == lib.PinInCpp_FileNotOpen:
            self.code = "PinInCpp_FileNotOpen"
            self.message = "File not successfully opened"
        elif code == lib.PinInCpp_DeserBinaryVersionInvalidException:
            self.code = "PinInCpp_DeserBinaryVersionInvalidException"
            self.message = "Invalid binary file version"
        elif code == lib.PinInCpp_DeserOutOfRange:
            self.code = "PinInCpp_DeserOutOfRange"
            self.message = "out-of-range exceptions"
        elif code == lib.PinInCpp_DeserBadAlloc:
            self.code = "PinInCpp_DeserBadAlloc"
            self.message = "bad allocation"

    def __str__(self):
        return f"{self.code}: {self.message}"

class PinInInitException(Exception):
    '''PinIn初始化失败异常'''
    filename = None
    def __init__(self, filename):
        self.filename = filename
        pass
    def __str__(self):
        return f"PinInInitException: Please check if the {self.filename} file is valid"

class TreeSearcherInitException(Exception):
    '''TreeSearcher初始化失败异常'''
    filename = None
    def __init__(self, filename):
        self.filename = filename
        pass
    def __str__(self):
        return f"TreeSearcherInitException: Please check if the {self.filename} file is valid. Or check the PinIn object."

class PinIn:
    '''拼音的配置类'''
    cdata = None
    def __init__(self, path:str):
        self.cdata = _create_pinin(lib.PinInCpp_PinIn_New(path.encode("utf-8")))
        if self.cdata == None:
            raise PinInInitException(path)
    
    @staticmethod
    def deserialize(path:str, keyboard:Keyboard = Keyboard.NULLKeyboard)->PinIn:
        '''
        反序列化指定路径上的文件返回PinIn对象，keyboard为NULLKeyboard的时候加载默认的全拼
        '''
        pinin_getter = _pffi.new("PinInCpp_PinIn[1]")
        deser_error = lib.PinInCpp_PinIn_Deserialize(path.encode("utf-8"),keyboard,pinin_getter)
        if deser_error != lib.PinInCpp_DeserNormal:
            raise DeserializeException(deser_error)
        result = PinIn.__new__(PinIn)
        result.cdata = _create_pinin(pinin_getter[0])
        return result

    def serialize(self, path:str)->bool:
        '''序列化PinIn类到指定的路径上'''
        return lib.PinInCpp_PinIn_Serialize(self.cdata, path.encode("utf-8")) != 0

    def get_config(self)->PinInConfig:
        '''获取config对象以配置PinIn'''
        return PinInConfig(self)
    
    def is_empty(self)->bool:
        '''判断PinIn是否为空，其实一般来讲没什么用'''
        return lib.PinInCpp_PinIn_Empty(self.cdata) != 0
    
    def pre_cache_string(self, input_str:str):
        '''缓存输入的字符串中的汉字字符'''
        lib.PinInCpp_PinIn_PreCacheString(self.cdata, input_str.encode("utf-8"))

    def pre_null_pinyin_id_cache(self):
        '''将空拼音id的字符也缓存进去'''
        lib.PinInCpp_PinIn_PreNullPinyinIdCache(self.cdata)

    def is_char_cache_enabled(self)->bool:
        '''判断是否开启字符缓存'''
        return lib.PinInCpp_PinIn_IsCharCacheEnabled(self.cdata) != 0
    
    def set_char_cache(self, enable:bool):
        '''
        设置是否开启字符串缓存

        警告！！！关闭后可能会导致严重性能下降，而字符本身并不是内存占用大头
        '''
        lib.PinInCpp_PinIn_SetCharCache(self.cdata, enable and 1 or 0)


class TreeSearcher:
    '''用于搜索的搜索树'''
    cdata = None
    def __init__(self, logic:Logic, PathOrPinIn:str|PinIn):
        temp_handle = None
        if type(PathOrPinIn) == str:
            temp_handle = lib.PinInCpp_TreeSearcher_NewPath(logic, PathOrPinIn.encode("utf-8"))
        else:
            temp_handle = lib.PinInCpp_TreeSearcher_NewPinIn(logic, PathOrPinIn.cdata)
        self.cdata = _create_tree_searcher(temp_handle)
        if self.cdata == None:
            raise TreeSearcherInitException(PathOrPinIn)
    
    @staticmethod
    def deserialize(path:str, pinin:PinIn)->TreeSearcher:
        '''
        反序列化指定路径上的文件返回TreeSearcher对象，必须提供PinIn上下文
        '''
        tree_getter = _pffi.new("PinInCpp_TreeSearcher[1]")
        deser_error = lib.PinInCpp_TreeSearcher_Deserialize(path.encode("utf-8"),pinin.cdata,tree_getter)
        if deser_error != lib.PinInCpp_DeserNormal:
            raise DeserializeException(deser_error)
        result = TreeSearcher.__new__(TreeSearcher)
        result.cdata = _create_tree_searcher(tree_getter[0])
        return result
        

    def get_pinin(self):
        '''获取这个搜索树的PinIn上下文'''
        empty_pinin = PinIn.__new__(PinIn)
        empty_pinin.cdata = _create_pinin(lib.PinInCpp_TreeSearcher_GetPinIn(self.cdata))
        if empty_pinin.cdata == None:
            raise Exception("PinIn: nullptr error")
        return empty_pinin

    def serialize(self, path:str)->bool:
        '''序列化TreeSearcher类到指定的路径上'''
        return lib.PinInCpp_TreeSearcher_Serialize(self.cdata, path.encode("utf-8")) != 0

    def put_string(self, item:str) -> int:
        '''
        放入待搜索项
        
        :param self: self
        :param item: 待搜索项
        :type item: str
        :return: TreeSearcher内部的字符串id
        :rtype: int
        '''
        return lib.PinInCpp_TreeSearcher_PutString(self.cdata, item.encode("utf-8"))

    def execute_search(self, search_str:str)->list[str]:
        '''执行搜索并返回字符串数组'''
        resultData = lib.PinInCpp_TreeSearcher_ExecuteSearch(self.cdata, search_str.encode("utf-8"))
        resultData = ffi.gc(resultData, lib.PinInCpp_SearchResult_Free)

        bufSize = -1
        buf = None

        result = []
        resultSize = resultData.size

        if resultSize == 0:
            return result
        id_list = ffi.unpack(resultData.ids, resultSize)

        for id in id_list:
            size = lib.PinInCpp_TreeSearcher_GetStrSizeById(self.cdata, id) + 1

            if size > bufSize:
                bufSize = size * 2
                buf = ffi.new("char[]", bufSize)
            lib.PinInCpp_TreeSearcher_PutToCharBuf(self.cdata, id, buf, bufSize)
            result.append(ffi.string(buf).decode("utf-8"))
            
        return result
    
    def execute_search_get_ids(self, search_str:str)->list[int]:
        '''执行搜索并返回字符串id数组'''
        resultData = lib.PinInCpp_TreeSearcher_ExecuteSearch(self.cdata, search_str.encode("utf-8"))
        resultData = ffi.gc(resultData, lib.PinInCpp_SearchResult_Free)

        result = []
        resultSize = resultData.size

        if resultSize == 0:
            return result
        
        result = ffi.unpack(resultData.ids, resultSize)
        return result
    
    def get_str_by_id(self, id:int)->str:
        '''根据字符串id返回字符串'''
        cid = ffi.cast("size_t", id)
        size = lib.PinInCpp_TreeSearcher_GetStrSizeById(self.cdata, cid) + 1
        buf = ffi.new("char[]", size)
        lib.PinInCpp_TreeSearcher_PutToCharBuf(self.cdata, cid, buf, size)
        return ffi.string(buf).decode("utf-8")
    
    def get_str_list_by_ids(self, ids:list[int])->list[str]:
        '''根据字符串id数组返回字符串数组'''
        result = []
        bufSize = -1
        buf = None
        for id in ids:
            cid = ffi.cast("size_t", id)
            size = lib.PinInCpp_TreeSearcher_GetStrSizeById(self.cdata, cid) + 1
            if size > bufSize:
                bufSize = size * 2
                buf = ffi.new("char[]", bufSize)
            lib.PinInCpp_TreeSearcher_PutToCharBuf(self.cdata, cid, buf, bufSize)
            result.append(ffi.string(buf).decode("utf-8"))
        return result
    
    def str_pool_reserve(self, newcapacity:int):
        '''扩容TreeSearcher内部的字符串池的大小，通常不需要手动调用'''
        lib.PinInCpp_TreeSearcher_StrPoolReserve(self.cdata, ffi.cast("size_t", newcapacity))

    def refresh(self):
        '''强制PinIn提交的配置现在就要刷新'''
        lib.PinInCpp_TreeSearcher_Refresh(self.cdata)

    def shrink_to_fit(self):
        '''减少TreeSearcher中多余分配的内存，可以收缩内存占用'''
        lib.PinInCpp_TreeSearcher_ShrinkToFit(self.cdata)
