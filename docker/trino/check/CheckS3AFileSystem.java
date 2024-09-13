// javac CheckS3AFileSystem.java
// java -cp . CheckS3AFileSystem

public class CheckS3AFileSystem {
    public static void main(String[] args) {
        try {
            // Try to load the S3AFileSystem class
            Class<?> clazz = Class.forName("org.apache.hadoop.fs.s3a.S3AFileSystem");
            System.out.println("Hello, World! S3AFileSystem class is available: " + clazz.getName());
        } catch (ClassNotFoundException e) {
            // If the class is not found, print an error message
            System.out.println("Hello, World! S3AFileSystem class not found!");
        }
    }
}
