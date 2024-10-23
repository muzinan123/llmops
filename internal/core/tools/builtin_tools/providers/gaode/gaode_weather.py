#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import Any, Type

import requests
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attribute


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="xxxxxxxxx")


class GaodeWeatherTool(BaseTool):
    name = "gaode_weather"
    description = "xxxxxxxxx"
    args_schema: Type[BaseModel] = GaodeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> str:
        try:
            gaode_api_key = os.getenv("GAODE_API_KEY")
            if not gaode_api_key:
                return f"xxxxxxx"

            city = kwargs.get("city", "")
            api_domain = "https://restapi.amap.com/v3"
            session = requests.session()

            city_response = session.request(
                method="GET",
                url=f"{api_domain}/config/district?key={gaode_api_key}&keywords={city}&subdistrict=0",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            city_response.raise_for_status()
            city_data = city_response.json()
            if city_data.get("info") == "OK":
                ad_code = city_data["districts"][0]["adcode"]

                weather_response = session.request(
                    method="GET",
                    url=f"{api_domain}/weather/weatherInfo?key={gaode_api_key}&city={ad_code}&extensions=all",
                    headers={"Content-Type": "application/json; charset=utf-8"},
                )
                weather_response.raise_for_status()
                weather_data = weather_response.json()
                if weather_data.get("info") == "OK":
                    return json.dumps(weather_data)
            return f"xxx{city}xxxxx"
        except Exception as e:
            return f"xxx{kwargs.get('city', '')}xxxxx"


@add_attribute("args_schema", GaodeWeatherArgsSchema)
def gaode_weather(**kwargs) -> BaseTool:
    return GaodeWeatherTool()
