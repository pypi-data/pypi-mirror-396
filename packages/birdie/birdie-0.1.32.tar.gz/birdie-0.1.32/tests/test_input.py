import pytest

from birdie.input import (
    BaseInput,
    InputGroup,
    InputString,
    InputNumber,
    InputInteger,
    InputRadio,
    InputMultiselect,
    InputFactSheet,
    InputFile,
    InputList,
)

def create_simple_schema() -> BaseInput:
    """Creates a schema using string, number, and integer types."""
    return InputGroup(
        title="Simple Data Form",
        description=(
            "Basic fields demonstrating string,number, and integer validation."
        ),
        values=[
            InputString(
                title="Username",
                description="Must be between 5-15 alphanumeric characters.",
                min_len=5,
                max_len=15,
                regex=r"^[a-zA-Z0-9]+$",
                placeholder="e.g., janedoe99",
                default="guest",
            ),
            InputNumber(
                title="Price",
                description=(
                    "The product price (float allowed). Must be positive."
                ),
                min_val=0.01,
                placeholder="e.g., 49.99",
                required=True,
            ),
            InputInteger(
                title="Quantity",
                description="The number of items to order. Max is 100.",
                min_val=1,
                max_val=100,
                default=1,
            ),
            InputString(
                title="API Key (Uppercase)",
                description="A 20-character key that must be all uppercase.",
                min_len=20,
                max_len=20,
                upper=True,
                required=False,
            ),
        ],
    )

def create_middle_schema() -> BaseInput:
    """Creates a schema including radio, multiselect, and factsheet."""
    return InputGroup(
        title="Intermediate Data Form",
        description="Includes choice and file inputs.",
        values=[
            # String/Number/Integer from simple
            InputString(
                title="Full Name",
                description="Your first and last name.",
                placeholder="e.g., John Smith",
                required=True,
            ),
            InputInteger(
                title="Years Experience",
                description="Must be a non-negative integer.",
                min_val=0,
                default=0,
            ),
            # New types: Radio, Multiselect, FactSheet
            InputRadio(
                title="Subscription Tier",
                description="Choose your subscription level.",
                values=["Basic", "Standard", "Premium"],
                default="Standard",
            ),
            InputMultiselect(
                title="Preferred Contact Methods",
                description="Select 1 to 3 ways we can reach you.",
                values=["Email", "Phone", "SMS", "Post"],
                min_selections=1,
                max_selections=3,
            ),
            InputFactSheet(
                title="Source Data Factsheet",
                description=(
                    "Link to a factsheet from an authorized data group."
                ),
                data_groups=[101, 102],
                required=True,
            ),
            InputFile(
                title="Profile Picture",
                description="Upload an image file.",
                # Testing extension normalization
                filetypes=[".png", ".jpeg", "gif"],
                required=False,
            ),
        ],
    )

def create_advanced_schema() -> BaseInput:
    """Creates a schema with nested InputGroup and InputList."""
    # Define a reusable child group for a list
    user_detail_group = InputGroup(
        title="Contact Detail",
        description="A single contact entry.",
        values=[
            InputString(
                title="Email",
                description="The user's email address.",
                regex=r"[^@]+@[^@]+\.[^@]+",
            ),
            InputNumber(
                title="Hourly Rate",
                description="The person's rate, must be > 10.",
                min_val=10.01,
                required=False,
            ),
            InputRadio(
                title="Status",
                description="Current employment status.",
                values=["Active", "Inactive"],
                default="Active",
            ),
        ],
    )

    return InputGroup(
        title="Advanced Application Form",
        description="A form demonstrating complex nested structures.",
        values=[
            InputString(
                title="Company Name",
                description="The name of the organization.",
                min_len=2,
            ),
            InputFactSheet(
                title="Company's Financial Data",
                description="Required financial factsheet.",
                data_groups=[200],
            ),
            # Nested Group
            InputGroup(
                title="Administrative Contact",
                description="Key person's details.",
                values=[
                    InputString(
                        title="Name", description="Contact name.", min_len=3
                    ),
                    InputString(
                        title="Phone",
                        description="Contact phone.",
                        regex=r"^\d{10}$",
                    ),
                ],
            ),
            # List of complex objects
            InputList(
                title="Team Members",
                description="Add 1 to 5 team members with their details.",
                obj=user_detail_group,  # Uses the reusable group defined above
                min_items=1,
                max_items=5,
            ),
            InputMultiselect(
                title="Regions",
                description=(
                    "Select all applicable operational regions (up to all 3)."
                ),
                values=["North America", "Europe", "Asia"],
                min_selections=0,
                max_selections=3,
            ),
        ],
    )


def create_input_schema_depends():
    return InputGroup(
        title="Social Post Creator",
        description="Generate optimized LinkedIn posts (organic or paid) with optional AI-generated images.",
        values=[
            InputString(
                title="Topic",
                description="What is this post about? Be specific about the main subject or theme.",
                min_len=5,
                max_len=500,
                placeholder="e.g., Launching our new marine coating product line with 25-year durability",
                required=True,
            ),
            InputString(
                title="Key Points",
                description="Specific points or messages to include (optional)",
                min_len=0,
                max_len=1000,
                placeholder="e.g., 25-year guarantee, eco-friendly formula, proven on 500+ vessels",
                required=False,
            ),
            InputRadio(
                title="Image Option",
                description="Do you want to generate an image, upload one, or post without an image?",
                values=["Generate Image", "Upload Image", "No Image"],
                default="No Image",
                required=True,
            ),
            InputString(
                title="Reference Images",
                description="Optional reference images",
                min_len=5,
                max_len=500,
                required=False,
                depends_on={"Image Option" : ["Generate Image"], "Topic" : []}
            ),
            InputRadio(
                title="Image Size Preset",
                description="Target image size",
                values=["1:1", "16:9", "9:16"],
                default="1:1",
                required=False,
                depends_on={"Image Option" : ["Generate Image", "Upload Image"]}
            ),
            InputRadio(
                title="Safety Level",
                description="Content safety filtering",
                values=["standard", "strict"],
                default="standard",
                required=False,
                depends_on={"Image Option" : ["Generate Image"]}

            ),
            InputString(
                title="Upload Image",
                description="Upload your own image (only if 'Upload Image' selected)",
                min_len=5,
                max_len=500,
                required=False,
                depends_on={"Image Option" : ["Upload Image"]}
            ),
        ],
    )

depends_data_1 = {
    "Topic" : "A new employee at Birdie",
    "Image Option" : "Generate Image",
    "Reference Images" : "a picture of the new employee",
    "Image Size Preset" : "16:9",
    "Safety Level" : "strict",
    "Upload Image" : "I have uploaded an image",
}

depends_data_2 = {
    "Topic" : "A new employee at Birdie",
    "Image Option" : "Upload Image",
    "Reference Images" : "a picture of the new employee",
    "Image Size Preset" : "16:9",
    "Safety Level" : "strict",
    "Upload Image" : "I have uploaded an image",
}

depends_data_3 = {
    "Topic" : "A new employee at Birdie",
    "Image Option" : "No Image",
    "Reference Images" : "a picture of the new employee",
    "Image Size Preset" : "16:9",
    "Safety Level" : "strict",
    "Upload Image" : "I have uploaded an image",
}

depends_data_bad = {
    "Topic" : "",
    "Image Option" : "No Image",
    "Reference Images" : "a picture of the new employee",
    "Image Size Preset" : "16:9",
    "Safety Level" : "strict",
    "Upload Image" : "I have uploaded an image",
}


simple_data = {
    "Username": "validuser1",
    "Price": 125.50,
    "Quantity": 5,
    "API Key (Uppercase)": "ABCDEFGHIJKLMNOPQRST",
}


middle_data = {
    "Full Name": "Alice Tester",
    "Years Experience": 3,
    "Subscription Tier": "Premium",
    "Preferred Contact Methods": ["Email", "Phone"],
    "Source Data Factsheet": {"id": "FS-1234", "data_group_id": 102},
    "Profile Picture": "avatar.PNG",
}

advanced_data = {
    "Company Name": "Tech Corp",
    "Company's Financial Data": {"id": "FIN-456", "data_group_id": 200},
    "Administrative Contact": {"Name": "Bob", "Phone": "1234567890"},
    "Team Members": [
        {
            "Email": "jane@example.com",
            "Hourly Rate": 55.50,
            "Status": "Active",
        },
        {
            "Email": "ceo@bigcorp.com",
            "Hourly Rate": 100.00,
            "Status": "Inactive",
        },
    ],
    "Regions": ["Europe"],
}

@pytest.mark.asyncio
async def validate_form(form_generator, data):
    """Helper to reconstruct schema and validate data."""
    form = form_generator()
    reconstructed_form = BaseInput.reconstruct(form.schema())
    return await reconstructed_form.validate(data)

@pytest.mark.asyncio
async def test_simple_validation():
    """Test valid data passes for simple schema."""

    result = await validate_form(create_simple_schema, simple_data)
    assert result["Username"] == simple_data["Username"]
    assert result["Price"] == simple_data["Price"]
    assert result["Quantity"] == simple_data["Quantity"]
    assert result["API Key (Uppercase)"] == simple_data["API Key (Uppercase)"]
    bad_data = simple_data.copy()
    bad_data["Price"] = -10
    with pytest.raises(ValueError):
        await validate_form(create_simple_schema, bad_data)

@pytest.mark.asyncio
async def test_middle_validation():
    """Test valid data passes for middle schema."""
    result = await validate_form(create_middle_schema, middle_data)
    assert result["Full Name"] == middle_data["Full Name"]
    assert result["Subscription Tier"] == middle_data["Subscription Tier"]
    assert set(result["Preferred Contact Methods"]) == set(
        middle_data["Preferred Contact Methods"]
    )
    bad_data = middle_data.copy()
    bad_data["Preferred Contact Methods"] = []  # Less than min_selections
    with pytest.raises(ValueError):
        await validate_form(create_middle_schema, bad_data)

@pytest.mark.asyncio
async def test_advanced_validation():
    """Test valid data passes for advanced schema."""
    result = await validate_form(create_advanced_schema, advanced_data)
    assert result["Company Name"] == advanced_data["Company Name"]
    assert len(result["Team Members"]) == len(advanced_data["Team Members"])
    assert result["Administrative Contact"]["Name"] == "Bob"
    bad_data = advanced_data.copy()
    # Make a team member email invalid
    bad_data["Team Members"][0]["Email"] = "not-an-email"
    with pytest.raises(ValueError):
        await validate_form(create_advanced_schema, bad_data)


@pytest.mark.asyncio
async def test_depends_on():
    """Testing if the depends_on works with the input groups and validation"""
    result1 = await validate_form(create_input_schema_depends, depends_data_1)
    print(f"Result 1 : {result1}")
    assert result1["Topic"] == "A new employee at Birdie"
    assert result1["Image Option"] == "Generate Image"
    assert result1["Reference Images"] == "a picture of the new employee"
    assert "Upload Image" not in result1
    assert "Safety Level" in result1

    result2 = await validate_form(create_input_schema_depends, depends_data_2)
    print(f"Result 2 : {result2}")
    assert result2["Topic"] == "A new employee at Birdie"
    assert result2["Image Option"] == "Upload Image"
    assert result2["Upload Image"] == "I have uploaded an image"
    assert "Reference Images" not in result2
    assert "Safety Level" not in result2

    result3 = await validate_form(create_input_schema_depends, depends_data_3)
    print(f"Result 3 : {result3}")
    assert result3["Topic"] == "A new employee at Birdie"
    assert result3["Image Option"] == "No Image"
    assert "Reference Images" not in result3
    assert "Safety Level" not in result3
    assert "Upload Image" not in result3
    assert "Image Size Preset" not in result3

    with pytest.raises(ValueError):
        await validate_form(create_input_schema_depends, depends_data_bad)





