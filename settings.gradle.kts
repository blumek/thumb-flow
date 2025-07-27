rootProject.name = "thumb-flow"

include(
    ":upload-handler",
    ":image-resizer"
)

project(":upload-handler").projectDir = file("src/lambda/upload_handler")
project(":image-resizer").projectDir = file("src/lambda/image_resizer")
