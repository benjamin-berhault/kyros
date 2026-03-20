// javac CheckClassAvailability.java
// java CheckClassAvailability org.apache.hadoop.fs.s3a.S3AFileSystem

public class CheckClassAvailability {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("Please provide the fully qualified class name as an argument.");
            System.exit(1);
        }

        String className = args[0];

        try {
            Class<?> clazz = Class.forName(className);
            System.out.println("Class " + className + " is available: " + clazz);
        } catch (ClassNotFoundException e) {
            System.err.println("Class " + className + " not found!");
        }
    }
}
