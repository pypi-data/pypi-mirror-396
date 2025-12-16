"""Bike sales data models for bike insights workflow.

This module defines Pydantic models for bike sales data, including
various bike types, customer reviews, stock, and sales information.
"""

import json
from typing import List, Union

from pydantic import BaseModel, Field

from ingenious.utils.model_utils import Listable_Object_To_Csv


class RootModel_Bike(BaseModel):
    """Base model for bike information.

    Attributes:
        brand: The bike brand name.
        model: The bike model name.
        year: The manufacturing year.
        price: The bike price.
    """

    brand: str
    model: str
    year: int
    price: float


class RootModel_MountainBike(RootModel_Bike):
    """Mountain bike model with suspension information.

    Attributes:
        suspension: Type of suspension (e.g., full, hardtail).
    """

    suspension: str = Field(..., description="Type of suspension (e.g., full, hardtail)")


class RootModel_RoadBike(RootModel_Bike):
    """Road bike model with frame material information.

    Attributes:
        frame_material: Material of the frame (e.g., carbon, aluminum).
    """

    frame_material: str = Field(..., description="Material of the frame (e.g., carbon, aluminum)")


class RootModel_CustomerReview(BaseModel):
    """Customer review model.

    Attributes:
        rating: The review rating score.
        comment: The review comment text.
    """

    rating: float
    comment: str


class RootModel_ElectricBike(RootModel_Bike):
    """Electric bike model with battery and motor specifications.

    Attributes:
        battery_capacity: Battery capacity in kWh.
        motor_power: Motor power in watts.
    """

    battery_capacity: float = Field(..., description="Battery capacity in kWh")
    motor_power: float = Field(..., description="Motor power in watts")


class RootModel_BikeStock(BaseModel):
    """Bike stock information.

    Attributes:
        bike: The bike instance (mountain, road, or electric).
        quantity: The quantity in stock.
    """

    bike: Union[RootModel_MountainBike, RootModel_RoadBike, RootModel_ElectricBike]
    quantity: int


class RootModel_BikeSale(BaseModel):
    """Bike sale record.

    Attributes:
        product_code: The product code.
        quantity_sold: The quantity sold.
        sale_date: The date of sale.
        year: The year of sale.
        month: The month of sale.
        customer_review: The associated customer review.
    """

    product_code: str
    quantity_sold: int
    sale_date: str
    year: int
    month: str
    customer_review: RootModel_CustomerReview


class RootModel_BikeSale_Extended(RootModel_BikeSale):
    """Extended bike sale record with store information.

    Attributes:
        store_name: The name of the store.
        location: The store location.
    """

    store_name: str
    location: str


class RootModel_Store(BaseModel):
    """Store model with sales and stock information.

    Attributes:
        name: The store name.
        location: The store location.
        bike_sales: List of bike sales records.
        bike_stock: List of bike stock records.
    """

    name: str
    location: str
    bike_sales: List[RootModel_BikeSale]
    bike_stock: List[RootModel_BikeStock]


class RootModel(BaseModel):
    """Root model for bike sales data.

    Attributes:
        stores: List of store records.
    """

    stores: List[RootModel_Store]

    @staticmethod
    def load_from_json(json_data: str) -> None:
        """Load bike sales data from JSON string.

        Args:
            json_data: JSON string containing bike sales data.
        """
        data = json.loads(json_data)
        root_model = RootModel(**data)
        print(root_model)

    def display_bike_sales_as_table(self) -> str:
        """Display bike sales data as a formatted table.

        Converts all bike sales records from all stores into an extended
        format with store information, then formats as a CSV table with
        a markdown heading.

        Returns:
            A markdown-formatted string with sales data in CSV format.
        """
        table_data: list[RootModel_BikeSale_Extended] = []

        for store in self.stores:
            for sale in store.bike_sales:
                store_name = store.name
                location = store.location
                rec = RootModel_BikeSale_Extended(
                    store_name=store_name, location=location, **sale.model_dump()
                )
                table_data.append(rec)

        ret = Listable_Object_To_Csv(table_data, RootModel_BikeSale_Extended)
        # Note always provide tabular data with a heading as this allows our datatables extension to render the data correctly
        return "## Sales\n" + ret
