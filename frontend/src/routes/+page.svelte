<script lang="ts">
    type DisarmResult = {
        id: string;
        backendName: string;
        format: string;
        originalSize: number;
        finalSize: number;
        imageSrc?: string;
    };

    let files = $state<FileList | null>(null);
    let loading = $state(false);
    let results = $state<DisarmResult[]>([]);
    let error = $state<string | null>(null);
    let currentOriginalSrc = $state<string | null>(null);
    let currentOriginalSize = $state<number>(0);

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
        loading = true;
        error = null;
        results = [];

        currentOriginalSrc = URL.createObjectURL(file);
        currentOriginalSize = file.size;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const promises = backends.map(async (backend) => {
                const response = await fetch(`http://localhost:${backend.port}/disarm`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (!response.ok || data.error) {
                    throw new Error(`${backend.name}: ${data.error || `HTTP error ${response.status}`}`);
                }

                return {
                    id: crypto.randomUUID(),
                    backendName: backend.name,
                    format: data.format,
                    originalSize: data.originalSize,
                    finalSize: data.finalSize,
                    imageSrc: data.disarmedFileBase64 ? `data:image/${data.format.toLowerCase()};base64,${data.disarmedFileBase64}` : undefined,
                } as DisarmResult;
            });

            const settled = await Promise.allSettled(promises);
            
            const newResults: DisarmResult[] = [];
            let errorMessages: string[] = [];
            
            for (const result of settled) {
                if (result.status === 'fulfilled') {
                    newResults.push(result.value);
                } else {
                    errorMessages.push(result.reason.message || String(result.reason));
                }
            }

            results = newResults;
            
            if (errorMessages.length > 0) {
                error = "Some backends failed: " + errorMessages.join(" | ");
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

<div class="min-h-screen bg-[#0a192f] text-white p-8 font-sans">
    <div class="max-w-7xl mx-auto space-y-8">
        <header class="text-center space-y-4">
            <h1 class="text-5xl font-extrabold tracking-tight text-white transition-all duration-500 hover:scale-[1.02]">
                Gatekeeper CDR Testbed
            </h1>
            <p class="text-blue-200 text-lg">Multi-Language Zero-Trust File Sanitization Engine</p>
        </header>

        <div class="bg-white text-[#0a192f] p-8 border-4 border-white transition-all duration-300 hover:-translate-y-1">
            <h2 class="text-2xl font-bold mb-6 uppercase tracking-wider">Upload Suspicious File</h2>
            <div class="space-y-6">
                <div class="border-4 border-dashed border-[#0a192f] p-8 text-center transition-all duration-300 hover:bg-gray-100 cursor-pointer relative">
                    <input type="file" bind:files class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"/>
                    <div class="font-bold text-lg">{files && files.length > 0 ? files[0].name : 'Click or drag file here'}</div>
                </div>
                
                <button 
                    onclick={handleUpload}
                    disabled={!files || loading}
                    class="w-full py-4 font-bold text-xl uppercase tracking-wider transition-all duration-300 transform {files && !loading ? 'bg-[#0a192f] text-white hover:-translate-y-1 hover:bg-blue-900' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}"
                >
                    {loading ? 'Disarming on all backends...' : 'Sanitize File'}
                </button>
            </div>
        </div>

        {#if error}
            <div class="bg-red-600 p-6 text-white border-4 border-red-800 transition-all duration-300 animate-pulse">
                <h3 class="font-bold text-xl mb-2 uppercase tracking-wider flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Error Disarming File
                </h3>
                <p class="font-mono text-sm break-all">{error}</p>
            </div>
        {/if}

        {#if currentOriginalSrc}
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12 items-start">
                <!-- Original Image View (Fixed side) -->
                <div class="bg-[#0a192f] p-8 border-4 border-red-500/50 sticky top-8 transition-all duration-300">
                    <h2 class="text-3xl font-bold mb-6 uppercase tracking-wider flex items-center text-red-400">
                        <svg class="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                        Original (Suspicious)
                    </h2>
                    <div class="mb-4 text-red-300 text-lg font-bold">Size: {(currentOriginalSize / 1024).toFixed(2)} KB</div>
                    <!-- REMOVED opacity-80 and grayscale-20 so it matches the sanitized images perfectly -->
                    <img src={currentOriginalSrc} alt="Original" class="max-w-full h-auto border-2 border-red-500/30" />
                </div>

                <!-- Scrollable Sanitized Results View (Vertical scrolling list) -->
                <div class="space-y-8 h-screen overflow-y-auto pr-4 custom-scrollbar">
                    {#if loading && results.length === 0}
                        <div class="flex justify-center items-center h-48">
                            <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
                        </div>
                    {/if}
                    
                    {#each results as res (res.id)}
                    <div class="bg-[#0a192f] p-8 border-4 border-green-500/50 transition-all duration-500 hover:-translate-y-1 relative overflow-hidden group">
                        <h2 class="text-2xl font-bold mb-6 uppercase tracking-wider flex items-center text-white">
                            <svg class="w-6 h-6 mr-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            Sanitized by {res.backendName}
                        </h2>
                        
                        <div class="grid grid-cols-2 gap-4 mb-6 text-white">
                            <div class="border-2 border-green-500/30 p-3 transition-all duration-300">
                                <div class="text-xs text-green-300 mb-1 uppercase tracking-wider font-bold">Clean Size</div>
                                <div class="text-xl font-bold text-green-400">{(res.finalSize / 1024).toFixed(2)} KB</div>
                            </div>
                            <div class="border-2 border-blue-500/30 p-3 transition-all duration-300">
                                <div class="text-xs text-blue-300 mb-1 uppercase tracking-wider font-bold">Difference</div>
                                {#if res.finalSize <= res.originalSize}
                                    <div class="text-xl font-bold text-blue-400">-{(((res.originalSize - res.finalSize) / res.originalSize) * 100).toFixed(1)}%</div>
                                    <div class="text-xs text-blue-300 mt-1">Smaller</div>
                                {:else}
                                    <div class="text-xl font-bold text-yellow-400">+{(((res.finalSize - res.originalSize) / res.originalSize) * 100).toFixed(1)}%</div>
                                    <div class="text-xs text-yellow-300 mt-1">Re-encode overhead</div>
                                {/if}
                            </div>
                        </div>
                        
                        {#if res.imageSrc}
                            <div class="border-2 border-green-500/50 p-2 bg-green-500/5">
                                <img src={res.imageSrc} alt="Sanitized by {res.backendName}" class="max-w-full h-auto" />
                            </div>
                        {/if}
                    </div>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</div>

<style>
    .custom-scrollbar::-webkit-scrollbar {
        width: 8px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: #0a192f;
        border-radius: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #1e3a8a;
        border-radius: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: #3b82f6;
    }
</style>
