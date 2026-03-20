After modifying the code to add the `X-Frame-Options` header, you'll need to build MinIO from the modified source and create a Docker image that includes your changes. Here’s how you can proceed step-by-step:

---

### **Step 1: Modify the Source Code**

1. Open the file where the `addCustomHeadersMiddleware` function is defined (in your uploaded file, it is `cmd/generic-handlers.go`).

2. Add the following line to include the `X-Frame-Options` header:

   ```go
   header.Set("X-Frame-Options", "ALLOWALL")  // Or use SAMEORIGIN or ALLOW-FROM <uri>
   ```

   The updated function should look something like this:

   ```go
   func addCustomHeadersMiddleware(h http.Handler) http.Handler {
       return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
           header := w.Header()
           header.Set("X-XSS-Protection", "1; mode=block")    // Prevents against XSS attacks
           header.Set("X-Content-Type-Options", "nosniff")    // Prevent mime-sniff
           header.Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains") // HSTS mitigates variants of MITM attacks
           header.Set("X-Frame-Options", "ALLOWALL")  // Allow embedding
           h.ServeHTTP(w, r)
       })
   }
   ```

3. Save your changes.

---

### **Step 2: Build MinIO**

Once you've modified the source code, follow these steps to build MinIO:

1. **Ensure Go is Installed**:
   You’ll need Go installed on your system. Run the following command to verify:

   ```bash
   go version
   ```

   If you don’t have Go installed, download it from the [official Go website](https://go.dev/dl/).

2. **Navigate to the MinIO Directory**:

   If you haven’t cloned the MinIO repository yet, do so with the following command:

   ```bash
   git clone https://github.com/minio/minio.git
   cd minio
   ```

3. **Build MinIO**:

   To build the MinIO server with your changes, run the following commands:

   ```bash
   make
   ```

   Or you can use `go build`:

   ```bash
   go build -o minio
   ```

4. **Verify the Build**:
   
   After the build is complete, ensure that the `minio` binary has been created in the current directory:

   ```bash
   ls -l minio
   ```

   Make sure the binary is executable:

   ```bash
   chmod +x minio
   ```

---

### **Step 3: Build a Docker Image**

Now that you’ve built the MinIO binary, the next step is to create a Docker image.

1. **Create a Dockerfile** in your MinIO directory.

   ```bash
   touch Dockerfile
   ```

2. **Add the Following Content** to the `Dockerfile`:

   ```Dockerfile
   FROM debian:bullseye-slim

   # Install necessary packages
   RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

   # Copy the custom MinIO binary to the image
   COPY minio /usr/local/bin/minio

   # Create the data directory
   RUN mkdir -p /data

   # Expose MinIO default and console ports
   EXPOSE 9000
   EXPOSE 9001

   # Set the entrypoint to start MinIO
   ENTRYPOINT ["minio"]

   # Default command to run MinIO in server mode
   CMD ["server", "/data", "--console-address", ":9001"]
   ```

   This Dockerfile:

   - Uses a slim Debian image as the base.
   - Copies your custom-built `minio` binary into the image.
   - Exposes the default MinIO server port (`9000`) and the console port (`9001`).

3. **Build the Docker Image**:

   Run the following command in the same directory as your `Dockerfile` to build the Docker image:

   ```bash
   docker build -t custom-minio .
   ```

   This will create a Docker image named `custom-minio` with your modified MinIO binary.

---

### **Step 4: Run the Custom MinIO Docker Image**

After building the Docker image, you can run your custom MinIO server in a Docker container:

1. **Run the Docker Container**:

   ```bash
   docker run -d -p 9000:9000 -p 9001:9001 --name custom-minio -e MINIO_ROOT_USER=admin -e MINIO_ROOT_PASSWORD=secretpassword custom-minio
   ```

   This command:
   - Runs your custom MinIO image in detached mode.
   - Maps ports `9000` and `9001` on the host to the container’s ports.
   - Sets the `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` environment variables.

2. **Verify the MinIO Service**:

   You can check if the MinIO service is running by visiting:

   - MinIO Console: [http://localhost:9001](http://localhost:9001)
   - MinIO Server: [http://localhost:9000](http://localhost:9000)

3. **Check the Headers**:

   Run the following command to verify that the `X-Frame-Options` header is now set as expected:

   ```bash
   curl -I http://localhost:9001
   ```

   You should see:

   ```
   X-Frame-Options: ALLOWALL
   ```

---

### **Step 5: Push the Custom Docker Image (Optional)**

If you want to push the custom image to a Docker registry (e.g., Docker Hub or a private registry), you can do so with the following commands:

1. **Tag the Image**:

   ```bash
   docker tag custom-minio your-dockerhub-username/custom-minio
   ```

2. **Push the Image**:

   ```bash
   docker push your-dockerhub-username/custom-minio
   ```

   Replace `your-dockerhub-username` with your actual Docker Hub username.

---

### **Summary**

1. Modify the source code by adding the `X-Frame-Options` header.
2. Build MinIO using `make` or `go build`.
3. Create a Dockerfile to package your custom-built MinIO into a Docker image.
4. Build the Docker image and run it.
5. Verify that the headers are correctly set using `curl`.

---

Let me know if you encounter any issues or need further clarification at any step!