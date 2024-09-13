// javac ListLoadedJars.java
// java -cp . ListLoadedJars

import java.util.Arrays;

public class ListLoadedJars {
    public static void main(String[] args) {
        // Get the classpath from the system property
        String classPath = System.getProperty("java.class.path");

        // Split the classpath into individual paths
        String[] paths = classPath.split(System.getProperty("path.separator"));

        // Print each path
        Arrays.stream(paths).forEach(System.out::println);
    }
}
