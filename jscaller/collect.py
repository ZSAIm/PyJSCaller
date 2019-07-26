

JSON = [
    # Method:
    'stringify', 'parse'
]


Math = [
    # Attribute:
    'E', 'LN2', 'LN10', 'LOG2E', 'LOG10E', 'PI', 'SQET1_2', 'SQRT2',
    # Method:
    'abs', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'exp', 'float', 'log', 'max', 'min', 'pow',
    'random', 'round', 'sin', 'sqrt', 'tan'
]


Boolean = [
    # Attribute:
    'constructor', 'prototype',
    # Method:
    'toString', 'valueOf'
]

Array = [
    # Attribute:
    'constructor', 'length', 'prototype',
    # Method:
    'concat', 'copyWithin', 'entries', 'every', 'fill', 'filter', 'find', 'findIndex', 'forEach', 'from',
    'includes', 'indexOf', 'isArray', 'join', 'keys', 'lastIndexOf', 'map', 'pop', 'push', 'reduce',
    'reduceRight', 'reverse', 'shift', 'slice', 'some', 'sort', 'splice', 'toString', 'unshift', 'valueOf'
]

Number = [
    # Attribute:
    'constructor', 'MAX_VALUE', 'MIN_VALUE', 'NEGATIVE_INFINITY', 'NaN', 'POSITIVE_INFINITY', 'prototype',
    # Method:
    'isFinite', 'toExponential', 'toFixed', 'toPrecision', 'toString', 'valueOf', 'isInteger', 'isSafeInteger'
]

String = [
    # Attribute:
    'constructor', 'length', 'prototype',
    # Method:
    'charAt', 'charCodeAt', 'concat', 'fromCharCode', 'indexOf', 'includes', 'lastIndexOf', 'match',
    'repeat', 'replace', 'search', 'slice', 'split', 'startsWith', 'substr', 'substring', 'toLowerCase',
    'toUpperCase', 'trim', 'toLocaleLowerCase', 'toLocaleUpperCase', 'valueOf', 'toString'
]


Date = [
    # Attribute:
    'constructor', 'prototype',
    # Method:
    'getDate', 'getDay', 'getFullYear', 'getHours', 'getMinutes', 'getMonth', 'getSeconds', 'getTime',
    'getTimezoneOffset', 'getUTCDate', 'getUTCDay', 'getUTCFullYear', 'getUTCHours', 'getUTCMilliseconds',
    'getUTCMinutes', 'getUTCMonth', 'getUTCSeconds', 'getYear', 'parse', 'setDate', 'setFullYear',
    'setHours', 'setMilliseconds', 'setMinutes', 'setMonth', 'setSeconds', 'setTime', 'setUTCDate',
    'setUTCFullYear', 'setUTCHours', 'setUTCMilliseconds', 'setUTCMinutes', 'setUTCMonth', 'setUTCSeconds',
    'setYear', 'toDateString', 'toGMTString', 'toISOString', 'toJSON', 'toLocaleDateString',
    'toLocaleTimeString', 'toLocaleString', 'toString', 'toTimeString', 'toUTCString', 'UTC', 'valueOf'

]


RegExp = [
    # Attribute:
    'constructor', 'global', 'ignoreCase', 'lastIndex', 'multiline', 'source'
    # Method:
    'compile', 'exec', 'test', 'toString'

]


Infinity = []
NaN = []
undefined = []
decodeURI = []
decodeURIComponent = []
encodeURI = []
encodeURIComponent = []
escape = []
eval = []
isFinite = []
isNaN = []
parseFloat = []
parseInt = []
unescape = []

require = []

OBJECT = {
    'JSON': JSON,
    'Math': Math,
    'Boolean': Boolean,
    'Array': Array,
    'Number': Number,
    'String': String,
    'Date': Date,
    'RegExp': RegExp,
    'Infinity': Infinity,
    'NaN': NaN,
    'undefined': undefined,
    'decodeURI': decodeURI,
    'decodeURIComponent': decodeURIComponent,
    'encodeURI': encodeURI,
    'encodeURIComponent': encodeURIComponent,
    'escape': escape,
    'eval': eval,
    'isFinite': isFinite,
    'isNaN': isNaN,
    'parseFloat': parseFloat,
    'parseInt': parseInt,
    'unescape': unescape,
    'require': require

}


def _self_extracting():
    from jscaller.express import Object
    for i, j in OBJECT.items():
        obj = Object(None, i)
        for m in j:
            subobj = obj.get(m)
            obj.sub(subobj)
        _self_extracting.__globals__[i] = obj
        OBJECT[i] = obj


_self_extracting()

del _self_extracting


def new(expr):
    expr.result.new()
    return expr