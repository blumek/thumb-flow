import org.gradle.api.model.ObjectFactory
import org.gradle.api.provider.ListProperty
import org.gradle.api.provider.MapProperty
import org.gradle.api.provider.Property
import org.gradle.kotlin.dsl.listProperty
import org.gradle.kotlin.dsl.mapProperty
import org.gradle.kotlin.dsl.property
import javax.inject.Inject

open class LocalStackExtension @Inject constructor(objects: ObjectFactory) {
    val containerName: Property<String> = objects.property<String>()
        .convention("localstack-container")

    val port: Property<Int> = objects.property<Int>()
        .convention(4566)

    val services: Property<String> = objects.property<String>()
        .convention("s3")

    val region: Property<String> = objects.property<String>()
        .convention("us-east-1")

    val accessKeyId: Property<String> = objects.property<String>()
        .convention("test")

    val secretAccessKey: Property<String> = objects.property<String>()
        .convention("test")

    val buckets: ListProperty<String> = objects.listProperty<String>()
        .convention(emptyList())

    val testEnvironmentVariables: MapProperty<String, String> = objects.mapProperty<String, String>()
        .convention(emptyMap())
}
