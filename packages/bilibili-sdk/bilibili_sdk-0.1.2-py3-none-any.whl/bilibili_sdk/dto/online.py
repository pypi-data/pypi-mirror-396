#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseResponse


class Online(BaseModel):
    total: str = Field("1", title="")
    count: str = Field("1", title="")

    #  @property
    #  def online(self) -> int:
        #  """The online property."""
        #  online = 0
        #  if self.total:
            #  try:
                #  total = self.total.replace("+", "")
                #  online = int(total)
            #  except Exception:
                #  online = self.count
        #  if online >= 1000:
            #  online += self.count
        #  return online

class GetOnlineRes(BaseResponse):
    data: Optional[Online] = Field(None)
