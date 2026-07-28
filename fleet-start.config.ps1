# Per-repo fleet start config for gimp-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'gimp-mcp'
    BackendPort  = 10773
    FrontendPort = 10772
    HealthPath   = '/api/health'
    WebRoot      = 'D:\Dev\repos\gimp-mcp\webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'gimp_mcp.http_app:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10773' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
