# BookCoverService - Java Implementation

This is a Java conversion of the Python `BookCoverService` from the Finwise project. The service fetches book cover images from multiple sources with fallbacks.

## Features

- **Google Books API Integration**: Primary source for real book covers
- **OpenLibrary API Integration**: Secondary source for book covers
- **Fallback Placeholder Generation**: Creates text-based placeholders when APIs fail
- **Genre-specific Color Coding**: Different colors for different book genres
- **Error Handling**: Graceful fallbacks between different sources

## Requirements

- Java 11 or higher
- Maven 3.6+ (for building)

## Project Structure

```
├── BookCoverService.java    # Main service class
├── pom.xml                  # Maven configuration
└── README_Java.md          # This file
```

## Building the Project

### Using Maven (Recommended)

```bash
# Compile the project
mvn compile

# Create executable JAR
mvn package

# Run the service
java -jar target/book-cover-service-1.0.0.jar
```

### Using Java Compiler Directly

```bash
# Compile
javac BookCoverService.java

# Run
java BookCoverService
```

## Usage

### Basic Usage

```java
BookCoverService service = new BookCoverService();

// Get book cover URL
String coverUrl = service.getBookCover("Atomic Habits", "James Clear", "Self-Help");
System.out.println("Cover URL: " + coverUrl);
```

### API Sources

The service tries multiple sources in order:

1. **Google Books API** - Real book covers (primary source)
2. **OpenLibrary API** - Alternative book covers (secondary source)
3. **Placeholder Generator** - Text-based fallback with genre colors

### Genre Support

The service supports various genres with specific color coding:

- Business & Management: Dark blue-gray
- Psychology: Purple
- Self-Help: Green
- Finance: Red
- Investment: Orange
- Leadership: Blue
- And many more...

## Key Differences from Python Version

1. **No External Dependencies**: Uses only Java standard library
2. **Regex-based JSON Parsing**: Simple regex patterns instead of JSON libraries
3. **Functional Interface**: Uses Java 8+ functional interfaces for source methods
4. **Built-in HTTP Client**: Uses `HttpURLConnection` instead of requests library
5. **Exception Handling**: Java-style exception handling with try-catch blocks

## Testing

The main method includes basic testing:

```java
public static void main(String[] args) {
    BookCoverService service = new BookCoverService();
    
    String coverUrl = service.getBookCover("Atomic Habits", "James Clear", "Self-Help");
    System.out.println("Book cover URL: " + coverUrl);
    
    coverUrl = service.getBookCover("Rich Dad Poor Dad", "Robert Kiyosaki", "Personal Finance");
    System.out.println("Book cover URL: " + coverUrl);
}
```

## Error Handling

The service gracefully handles:
- Network timeouts
- API failures
- Invalid responses
- Missing data

Each source method has its own error handling, and the service continues to the next source if one fails.

## Performance Considerations

- **API Rate Limiting**: 200ms delay between API calls to be respectful
- **Connection Timeouts**: 10-second timeouts for HTTP requests
- **Fallback Strategy**: Quick fallback to next source on failure

## License

This Java implementation maintains the same functionality as the original Python service while following Java best practices and conventions. 