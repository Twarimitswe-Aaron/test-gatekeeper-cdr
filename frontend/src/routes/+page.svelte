<script lang="ts">
    type DisarmResult = {
        backendName: string;
        format: string;
        originalSize: number;
        finalSize: number;
        imageSrc?: string;
        originalImageSrc?: string;
    };

    let files = $state<FileList | null>(null);
    let selectedBackend = $state('node');
    let loading = $state(false);
    let results = $state<DisarmResult[]>([]);
    let error = $state<string | null>(null);

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

        const originalImageSrc = URL.createObjectURL(file);
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

            const newResult: DisarmResult = {
                backendName: backend.name,
                format: data.format,
                originalSize: data.originalSize,
                finalSize: data.finalSize,
                imageSrc: data.disarmedFileBase64 ? `data:image/${data.format.toLowerCase()};base64,${data.disarmedFileBase64}` : undefined,
                originalImageSrc: originalImageSrc
            };

            // Prepend so the newest result is always at the top
            results = [newResult, ...results];

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
    <div class="max-w-4xl mx-auto space-y-8">
        <header class="text-center space-y-4">
            <h1 class="text-5xl font-extrabold tracking-tight text-white transition-all duration-500 hover:scale-[1.02]">
                Gatekeeper CDR Testbed
            </h1>
            <p class="text-blue-200 text-lg">Multi-Language Zero-Trust File Sanitization Engine</p>
        </header>

        <div class="bg-white text-[#0a192f] p-8 border-4 border-white transition-all duration-300 hover:-translate-y-1">
            <h2 class="text-2xl font-bold mb-6 uppercase tracking-wider">1. Select Target Backend</h2>
            <div class="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-5 gap-4">
                {#each backends as backend (backend.id)}
                    <button 
                        class="p-4 border-2 transition-all duration-300 transform hover:-translate-y-1 hover:bg-[#0a192f] hover:text-white {selectedBackend === backend.id ? 'border-[#0a192f] bg-[#0a192f] text-white' : 'border-[#0a192f] bg-transparent text-[#0a192f]'}"
                        onclick={() => selectedBackend = backend.id}
                    >
                        <div class="font-bold">{backend.name}</div>
                        <div class="text-sm opacity-80">Port {backend.port}</div>
                    </button>
                {/each}
            </div>
        </div>

        <div class="bg-white text-[#0a192f] p-8 border-4 border-white transition-all duration-300 hover:-translate-y-1">
            <h2 class="text-2xl font-bold mb-6 uppercase tracking-wider">2. Upload Suspicious File</h2>
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
                    {loading ? 'Disarming...' : 'Sanitize File'}
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

        {#if results.length > 0}
            <div class="space-y-8">
                {#each results as res (res.backendName)}
                <div class="bg-[#0a192f] p-8 border-4 border-white transition-all duration-500 hover:-translate-y-2 relative overflow-hidden group">
                    <div class="absolute inset-0 bg-white opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>
                    <h2 class="text-3xl font-bold mb-8 uppercase tracking-wider flex items-center text-white">
                        <svg class="w-8 h-8 mr-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        Sanitized by {res.backendName}
                    </h2>
                    
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8 text-white">
                        <div class="border-2 border-white/20 p-4 transition-all duration-300 hover:border-white">
                            <div class="text-sm text-blue-200 mb-1 uppercase tracking-wider font-bold">Format</div>
                            <div class="text-2xl font-bold">{res.format}</div>
                        </div>
                        <div class="border-2 border-red-500/50 p-4 transition-all duration-300 hover:border-red-500 hover:bg-red-500/10">
                            <div class="text-sm text-red-300 mb-1 uppercase tracking-wider font-bold">Original Size</div>
                            <div class="text-2xl font-bold text-red-400">{(res.originalSize / 1024).toFixed(2)} KB</div>
                        </div>
                        <div class="border-2 border-green-500/50 p-4 transition-all duration-300 hover:border-green-500 hover:bg-green-500/10">
                            <div class="text-sm text-green-300 mb-1 uppercase tracking-wider font-bold">Clean Size</div>
                            <div class="text-2xl font-bold text-green-400">{(res.finalSize / 1024).toFixed(2)} KB</div>
                        </div>
                        <div class="border-2 border-blue-500/50 p-4 transition-all duration-300 hover:border-blue-500 hover:bg-blue-500/10">
                            <div class="text-sm text-blue-300 mb-1 uppercase tracking-wider font-bold">Removed Metadata</div>
                            <div class="text-2xl font-bold text-blue-400">{(((res.originalSize - res.finalSize) / res.originalSize) * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                    
                    {#if res.imageSrc && res.originalImageSrc}
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-8">
                            <div class="border-2 border-red-500/30 p-4 flex flex-col items-center justify-center transition-all duration-300 hover:border-red-500">
                                <div class="text-sm text-red-400 mb-4 font-bold uppercase tracking-wider flex items-center">
                                    Original Image (Suspicious)
                                </div>
                                <img src={res.originalImageSrc} alt="Original" class="max-w-full max-h-[400px] opacity-80 grayscale-[20%]" />
                            </div>
                            <div class="border-2 border-green-500 p-4 flex flex-col items-center justify-center relative transition-all duration-300 hover:bg-green-500/5">
                                <div class="text-sm text-green-400 mb-4 font-bold uppercase tracking-wider flex items-center">
                                    Sanitized Image (Safe)
                                </div>
                                <img src={res.imageSrc} alt="Sanitized" class="max-w-full max-h-[400px] transition-transform duration-500 hover:scale-105" />
                            </div>
                        </div>
                    {/if}
                </div>
                {/each}
            </div>
        {/if}
    </div>
</div>
