# Emby API Documentation

## Official Documentation
- **Web API**: https://dev.emby.media/
- **GitHub Wiki**: https://github.com/MediaBrowser/Emby/wiki

## Key Endpoints Used

### Get Libraries (Media Folders)
```
GET /Library/MediaFolders
Headers:
  X-Emby-Token: your_api_key
```

### Get Items
```
GET /Items
Headers:
  X-Emby-Token: your_api_key
Parameters:
  ParentId: library_id
  IncludeItemTypes: Movie,Series,Book
  Limit: 100
  StartIndex: 0
```

### Get System Info
```
GET /System/Info
Headers:
  X-Emby-Token: your_api_key
```

### Search Items
```
GET /Items
Headers:
  X-Emby-Token: your_api_key
Parameters:
  SearchTerm: query
  Recursive: true
  Limit: 20
```

### Get Users
```
GET /Users
Headers:
  X-Emby-Token: your_api_key
```

### Get User Items
```
GET /Users/{UserId}/Items
Headers:
  X-Emby-Token: your_api_key
Parameters:
  IncludeItemTypes: CollectionFolder
```

## Authentication
All requests require the API key via header:
```
X-Emby-Token: your_api_key
```

## Response Format
Emby returns PascalCase field names:
- `Id`, `Name`, `Type`
- `CollectionType`, `Locations`
- `MediaType`, `PremiereDate`, etc.

## Notes
- No built-in Swagger UI
- Base URL: http://192.168.50.16:8096
- API key can be generated in Emby Server → API Keys
