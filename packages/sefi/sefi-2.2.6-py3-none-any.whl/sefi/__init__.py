# Copyright (C) 2025 Xiaoyang Chen - All Rights Reserved
# Licensed under the GNU GENERAL PUBLIC LICENSE Version 3
# Repository: https://github.com/xychcz/S3Fit
# Contact: s3fit@xychen.me

# export everything from s3fit so `import sefi` works the same.
from s3fit import * 

try:
    # reflect s3fit's version, if available
    from s3fit import __version__ as __version__
except Exception:
    # for the oldest version sefi required (__version__ not coded)
    __version__ = "2.2.4"