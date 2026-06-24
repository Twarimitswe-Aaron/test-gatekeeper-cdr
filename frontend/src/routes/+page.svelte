<script lang="ts">
    type DisarmResult = {
        format: string;
        originalSize: number;
        finalSize: number;
        disarmedFileBase64?: string;
    };

    let files = $state<FileList | null>(null);
    let selectedBackend = $state('node');
    let loading = $state(false);
    let result = $state<DisarmResult | null>(null);
    let error = $state<string | null>(null);
    let imageSrc = $state<string | null>(null);

    const backends = [
        { id: 'node', name: 'Node.js (Express)', port: 3001 },
        { id: 'go', name: 'Go', port: 3002 },
        { id: 'java', name: 'Java (Spring Boot)', port: 3003 },
        { id: 'php', name: 'PHP', port: 3004 },
        { id: 'python', name: 'Python (FastAPI)', port: 3005 }
    ];

    async function handleUpload() {
        if (!files || files.length === 0) {
            error = "Please select a file first.";
            return;
        }

        const file = files[0];
        const backend = backends.find(b => b.id === selectedBackend);
        if (!backend) return;

        loading = true;
        error = null;
        result = null;
        imageSrc = null;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`http://localhost:${backend.port}/disarm`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok || data.error) {
                throw new Error(data.error || `HTTP error ${response.status}`);
            }

            result = data as DisarmResult;
            
            // Reconstruct the image src
            if (result.disarmedFileBase64) {
                imageSrc = `data:image/${result.format.toLowerCase()};base64,${result.disarmedFileBase64}`;
            }

        } catch (err: unknown) {
            if (err instanceof Error) {
                error = err.message;
            } else {
                error = "An unknown error occurred.";
            }
        } finally {
            loading = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-900 text-white p-8 font-sans">
    <div class="max-w-4xl mx-auto space-y-8">
        <header class="text-center space-y-4">
            <h1 class="text-5xl font-extrabold tracking-tight bg-linear-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                Gatekeeper CDR Testbed
            </h1>
            <p class="text-gray-400 text-lg">Multi-Language Zero-Trust File Sanitization Engine</p>
        </header>

        <div class="bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-700">
            <h2 class="text-2xl font-semibold mb-4">1. Select Target Backend</h2>
            <div class="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-5 gap-4">
                {#each backends as backend (backend.id)}
                    <button 
                        class="p-4 rounded-xl border-2 transition-all duration-200 {selectedBackend === backend.id ? 'border-blue-500 bg-blue-500/20' : 'border-gray-600 bg-gray-700 hover:border-gray-500 hover:bg-gray-600'}"
                        onclick={() => selectedBackend = backend.id}
                    >
                        <div class="font-medium">{backend.name}</div>
                        <div class="text-sm text-gray-400">Port {backend.port}</div>
                    </button>
                {/each}
            </div>
        </div>

        <div class="bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-700">
            <h2 class="text-2xl font-semibold mb-4">2. Upload Suspicious File</h2>
            <div class="space-y-4">
                <div class="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:border-gray-500 transition-colors">
                    <input type="file" bind:files class="w-full cursor-pointer text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-500 file:text-white hover:file:bg-blue-600"/>
                </div>
                
                <button 
                    onclick={handleUpload}
                    disabled={!files || loading}
                    class="w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all {files && !loading ? 'bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white' : 'bg-gray-700 text-gray-500 cursor-not-allowed'}"
                >
                    {loading ? 'Disarming...' : 'Sanitize File'}
                </button>
            </div>
        </div>

        {#if error}
            <div class="bg-red-900/50 border border-red-500 rounded-xl p-6 text-red-200 shadow-lg">
                <h3 class="font-bold text-lg mb-2 flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Error Disarming File
                </h3>
                <p class="font-mono text-sm break-all">{error}</p>
            </div>
        {/if}

        {#if result}
            <div class="bg-gray-800 rounded-2xl p-6 shadow-xl border border-green-500/30">
                <h2 class="text-2xl font-semibold mb-6 flex items-center text-green-400">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Sanitization Successful
                </h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="space-y-4">
                        <div class="bg-gray-900 rounded-xl p-4 border border-gray-700">
                            <div class="text-sm text-gray-400 mb-1">Detected Format</div>
                            <div class="text-xl font-medium">{result.format}</div>
                        </div>
                        <div class="bg-gray-900 rounded-xl p-4 border border-gray-700">
                            <div class="text-sm text-gray-400 mb-1">Original Size</div>
                            <div class="text-xl font-medium text-red-400">{(result.originalSize / 1024).toFixed(2)} KB</div>
                        </div>
                        <div class="bg-gray-900 rounded-xl p-4 border border-gray-700">
                            <div class="text-sm text-gray-400 mb-1">Clean Size</div>
                            <div class="text-xl font-medium text-green-400">{(result.finalSize / 1024).toFixed(2)} KB</div>
                        </div>
                        <div class="bg-gray-900 rounded-xl p-4 border border-gray-700">
                            <div class="text-sm text-gray-400 mb-1">Payload Reduction</div>
                            <div class="text-xl font-medium text-blue-400">{(((result.originalSize - result.finalSize) / result.originalSize) * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                    
                    {#if imageSrc}
                        <div class="bg-gray-900 rounded-xl p-4 border border-gray-700 flex flex-col items-center justify-center min-h-[300px]">
                            <div class="text-sm text-gray-400 mb-4 self-start">Reconstructed Safe Image</div>
                            <img src={imageSrc} alt="Sanitized" class="max-w-full max-h-[400px] rounded-lg shadow-lg" />
                        </div>
                    {/if}
                </div>
            </div>
        {/if}
    </div>
</div>
