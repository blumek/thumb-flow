rootProject.name = "thumb-flow"

include(
    ":upload_handler",
    ":image_resizer"
)

project(":upload_handler").projectDir = file("src/lambda/upload_handler")
project(":image_resizer").projectDir = file("src/lambda/image_resizer")

