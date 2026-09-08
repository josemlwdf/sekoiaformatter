from datetime import datetime
import json
from pydantic import BaseModel, Field
from sekoia_automation.action import Action  


class FormatArguments(BaseModel):  
    template: str = Field(description="Template string with Python f-string style placeholders (e.g., 'Hello {name}!')")
    data: str = Field(description="JSON string containing the variables to format into the template (e.g., '{\"name\": \"value\"}')")


class FormatResponse(BaseModel):  
    formatted_text: str = Field(description="The formatted output text")


class FormatAction(Action):  
    """
    Action to format text using Python f-string style formatting with automatic epoch timestamp conversion
    """

    results_model = FormatResponse

    def run(self, arguments: FormatArguments) -> FormatResponse:  
        try:
            # Parse JSON string to dictionary
            data_dict = json.loads(arguments.data)
            
            self.log(  
                message=f"Formatting template with {len(data_dict)} variables", 
                level="info"
            )
            
            # Preprocess data: convert epoch timestamps to datetime objects
            processed_data = {}
            for key, value in data_dict.items():
                # If value is numeric and looks like an epoch timestamp, convert it
                if isinstance(value, (int, float)) and value > 1000000000:
                    try:
                        processed_data[key] = datetime.fromtimestamp(value)
                    except (ValueError, OSError):
                        processed_data[key] = value
                else:
                    processed_data[key] = value
            
            # Format the template using the processed data dictionary
            formatted_text = arguments.template.format(**processed_data)
            
            self.log(
                message="Template formatted successfully",
                level="info"
            )
            
            return FormatResponse(formatted_text=formatted_text)
            
        except json.JSONDecodeError as e:
            self.error(f"Invalid JSON in data field: {e}")
        except KeyError as e:
            self.error(f"Missing variable in data: {e}")
        except ValueError as e:
            self.error(f"Invalid template format: {e}")
        except Exception as e:
            self.error(f"Formatting error: {e}")