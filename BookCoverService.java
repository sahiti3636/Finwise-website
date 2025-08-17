import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class BookCoverService {
    /** Service to fetch book cover images from multiple sources with fallbacks */
    
    private final BookCoverSource[] sources;
    
    public BookCoverService() {
        this.sources = new BookCoverSource[] {
            this::getGoogleBooksCover,      // Primary source - real book covers
            this::getOpenLibraryCover,      // Secondary source - OpenLibrary
            this::getSimplePlaceholder      // Final fallback - simple text placeholder
        };
    }
    
    public String getBookCover(String title, String author, String genre) {
        /** Get book cover from multiple sources with fallbacks */
        for (int i = 0; i < sources.length - 1; i++) { // Exclude simple placeholder as it's the final fallback
            try {
                String coverUrl = sources[i].getCover(title, author, genre);
                if (coverUrl != null && !coverUrl.isEmpty()) {
                    return coverUrl;
                }
            } catch (Exception e) {
                System.err.println("Error fetching cover from " + sources[i].getClass().getSimpleName() + ": " + e.getMessage());
                continue;
            }
        }
        
        // Final fallback to simple placeholder
        return getSimplePlaceholder(title, author, genre);
    }
    
    private String getGoogleBooksCover(String title, String author, String genre) {
        /** Get book cover from Google Books API (free tier) - Primary source */
        try {
            // Try exact title + author first
            String searchQuery = (title + " " + author).replace(" ", "+");
            String searchUrl = "https://www.googleapis.com/books/v1/volumes?q=" + searchQuery + "&maxResults=1";
            
            String response = makeHttpRequest(searchUrl);
            if (response != null) {
                String coverUrl = extractGoogleBooksCover(response);
                if (coverUrl != null) {
                    return coverUrl;
                }
            }
            
            // If exact match fails, try just title
            searchQuery = title.replace(" ", "+");
            searchUrl = "https://www.googleapis.com/books/v1/volumes?q=" + searchQuery + "&maxResults=3";
            
            response = makeHttpRequest(searchUrl);
            if (response != null) {
                String coverUrl = extractGoogleBooksCover(response);
                if (coverUrl != null) {
                    return coverUrl;
                }
            }
            
            TimeUnit.MILLISECONDS.sleep(200); // Be respectful to the API
            return null;
            
        } catch (Exception e) {
            System.err.println("Google Books error for '" + title + "': " + e.getMessage());
            return null;
        }
    }
    
    private String extractGoogleBooksCover(String jsonResponse) {
        /** Extract cover URL from Google Books API response using regex */
        // Look for thumbnail URL in the response
        Pattern pattern = Pattern.compile("\"thumbnail\":\\s*\"([^\"]+)\"");
        Matcher matcher = pattern.matcher(jsonResponse);
        if (matcher.find()) {
            String coverUrl = matcher.group(1);
            // Convert to larger size for better quality
            return coverUrl.replace("zoom=1", "zoom=3");
        }
        return null;
    }
    
    private String getOpenLibraryCover(String title, String author, String genre) {
        /** Get book cover from OpenLibrary API - Secondary source */
        try {
            // Try exact title + author first
            String searchQuery = (title + " " + author).replace(" ", "+");
            String searchUrl = "https://openlibrary.org/search.json?title=" + searchQuery + "&limit=3";
            
            String response = makeHttpRequest(searchUrl);
            if (response != null) {
                String coverUrl = extractOpenLibraryCover(response);
                if (coverUrl != null) {
                    return coverUrl;
                }
            }
            
            // If exact match fails, try just title
            searchQuery = title.replace(" ", "+");
            searchUrl = "https://openlibrary.org/search.json?title=" + searchQuery + "&limit=3";
            
            response = makeHttpRequest(searchUrl);
            if (response != null) {
                String coverUrl = extractOpenLibraryCover(response);
                if (coverUrl != null) {
                    return coverUrl;
                }
            }
            
            TimeUnit.MILLISECONDS.sleep(200); // Be respectful to the API
            return null;
            
        } catch (Exception e) {
            System.err.println("OpenLibrary error for '" + title + "': " + e.getMessage());
            return null;
        }
    }
    
    private String extractOpenLibraryCover(String jsonResponse) {
        /** Extract cover ID from OpenLibrary API response using regex */
        // Look for cover_i in the response
        Pattern pattern = Pattern.compile("\"cover_i\":\\s*(\\d+)");
        Matcher matcher = pattern.matcher(jsonResponse);
        if (matcher.find()) {
            int coverId = Integer.parseInt(matcher.group(1));
            return "https://covers.openlibrary.org/b/id/" + coverId + "-L.jpg";
        }
        return null;
    }
    
    private String getSimplePlaceholder(String title, String author, String genre) {
        /** Generate a simple text-based placeholder as final fallback */
        // Get genre-specific colors
        Map<String, String> genreColors = new HashMap<>();
        genreColors.put("Business & Management", "1f2937"); // Dark blue-gray
        genreColors.put("Psychology", "7c3aed");           // Purple
        genreColors.put("Self-Help", "059669");            // Green
        genreColors.put("Finance", "dc2626");              // Red
        genreColors.put("Investment", "ea580c");           // Orange
        genreColors.put("Leadership", "2563eb");           // Blue
        genreColors.put("Entrepreneurship", "0891b2");     // Cyan
        genreColors.put("Personal Finance", "16a34a");     // Green
        genreColors.put("Mindset", "9333ea");              // Purple
        genreColors.put("Behavioral Economics", "be185d"); // Pink
        genreColors.put("Behavioral Science", "a855f7");   // Purple
        genreColors.put("Success", "f59e0b");              // Yellow
        genreColors.put("Productivity", "0d9488");         // Teal
        genreColors.put("Personal Development", "059669");  // Green
        genreColors.put("Company Analysis", "1e40af");     // Blue
        genreColors.put("Startup Strategy", "0891b2");     // Cyan
        genreColors.put("Innovation", "7c2d12");           // Brown
        genreColors.put("Business Model", "1e293b");       // Slate
        
        String color = genreColors.getOrDefault(genre, "1f2937");
        String[] titleWords = title.split(" ");
        StringBuilder titleText = new StringBuilder();
        
        // Take first 3 words
        for (int i = 0; i < Math.min(titleWords.length, 3); i++) {
            if (i > 0) titleText.append("+");
            titleText.append(titleWords[i]);
        }
        
        return "https://placehold.co/400x600/" + color + "/ffffff?text=" + titleText.toString() + "&font=montserrat";
    }
    
    private String makeHttpRequest(String urlString) throws IOException {
        /** Helper method to make HTTP GET requests */
        URL url = new URL(urlString);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        connection.setConnectTimeout(10000);
        connection.setReadTimeout(10000);
        
        int responseCode = connection.getResponseCode();
        if (responseCode == HttpURLConnection.HTTP_OK) {
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();
            return response.toString();
        } else {
            return null;
        }
    }
    
    // Functional interface for the source methods
    @FunctionalInterface
    private interface BookCoverSource {
        String getCover(String title, String author, String genre);
    }
    
    // Main method for testing
    public static void main(String[] args) {
        BookCoverService service = new BookCoverService();
        
        // Test the service
        String coverUrl = service.getBookCover("Atomic Habits", "James Clear", "Self-Help");
        System.out.println("Book cover URL: " + coverUrl);
        
        coverUrl = service.getBookCover("Rich Dad Poor Dad", "Robert Kiyosaki", "Personal Finance");
        System.out.println("Book cover URL: " + coverUrl);
    }
} 