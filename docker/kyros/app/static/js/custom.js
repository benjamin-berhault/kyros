function getRootDomain() {
    const hostname = window.location.hostname;

    // Split the hostname into parts
    const parts = hostname.split('.');
    
    // If there are more than two parts, assume the first part is a subdomain
    if (parts.length > 2) {
      return parts.slice(-2).join('.'); // Join the last two parts
    }
    
    // If only two parts, it's already the root domain
    return hostname;
}
  