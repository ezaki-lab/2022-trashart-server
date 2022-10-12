"""
分別のための学習データを集めるAPI
"""

from flask import Blueprint, Flask
from flask_restful import Api, Resource
from logger import logger
from services.inspector import content_type, json_scheme
from services.server import response as res
from utils.base64_to_file import Base64ToFile
from utils.random import generate_str

app = Blueprint("separate-train", __name__)
api = Api(app, errors=Flask.errorhandler)

class Separate(Resource):
    @logger
    @content_type("application/json")
    @json_scheme({
        "plastic_type (required)": str,
        "plastic_color (required)": str,
        "image_lighted (required)": str,
        "image_led850 (required)": str,
        "image_led940 (required)": str
    })
    def post(self, json: dict):
        color_map = {
            "white": "0",
            "gray": "1",
            "black": "2",
            "red": "3",
            "brown": "4",
            "yellow": "5",
            "green": "6",
            "blue": "7"
        }

        self.material_name = generate_str(8)
        filename = self.__generate_file_name(json["plastic_type"])

        led_names = [
            ["image_lighted", "lighted"],
            ["image_led850", "850"],
            ["image_led940", "940"]
        ]

        try:
            for led in led_names:
                saver = Base64ToFile(json[led[0]])
                saver.save(
                    self.__generate_folder_name(
                        color_map[json["plastic_color"]],
                        json["plastic_color"],
                        led[1]
                    ),
                    filename
                )

        except ValueError:
            return res.bad_request({
                "message": "This base64 image is not valid."
            })
        except KeyError:
            return res.bad_request({
                "message": "This color name is not valid."
            })

        return res.ok({})

    def __generate_folder_name(self, color_id: str, color_name: str, led_name) -> str:
        base_folder = "storage/separate-train"
        return "{}/{}.{}/{}".format(
                    base_folder,
                    color_id,
                    color_name,
                    led_name
                )

    def __generate_file_name(self, plastic_type: str) -> str:
        return "{}_{}.png".format(plastic_type, self.material_name)

api.add_resource(Separate, "/separate-train")
