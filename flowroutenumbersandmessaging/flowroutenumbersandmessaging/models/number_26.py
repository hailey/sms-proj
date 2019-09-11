# -*- coding: utf-8 -*-

"""
    flowroutenumbersandmessaging.models.number_26

    This file was automatically generated by APIMATIC v2.0 ( https://apimatic.io )
"""
import flowroutenumbersandmessaging.models.data_27

class Number26(object):

    """Implementation of the 'Number26' model.

    TODO: type model description here.

    Attributes:
        data (Data27): TODO: type description here.
        included (list of object): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "data" : "data",
        "included" : "included"
    }

    def __init__(self,
                 data=None,
                 included=None):
        """Constructor for the Number26 class"""

        # Initialize members of the class
        self.data = data
        self.included = included


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        data = flowroutenumbersandmessaging.models.data_27.Data27.from_dictionary(dictionary.get("data")) if dictionary.get("data") else None
        included = dictionary.get("included")

        # Return an object of this model
        return cls(data,
                   included)


