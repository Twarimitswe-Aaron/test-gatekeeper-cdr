<script lang="ts">
    type DisarmResult = {
        id: string;
        backendName: string;
        format: string;
        outputFormat: string;
        originalSize: number;
        finalSize: number;
        imageSrc?: string;
        pngImageSrc?: string;
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
        // Java (Spring Boot) — disabled: pending Maven Central publish
        // { id: 'java', name: 'Java (Spring Boot)', port: 3003 },
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
                    outputFormat: data.outputFormat || data.format,
                    originalSize: data.originalSize,
                    finalSize: data.finalSize,
                    imageSrc: data.disarmedFileBase64 ? `data:image/${(data.outputFormat || data.format).toLowerCase()};base64,${data.disarmedFileBase64}` : undefined,
                    pngImageSrc: data.pngFileBase64 
                        ? `data:image/png;base64,${data.pngFileBase64}` 
                        : (((data.outputFormat || data.format || '').toLowerCase() === 'png' && data.disarmedFileBase64) 
                            ? `data:image/png;base64,${data.disarmedFileBase64}` 
                            : undefined),
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

<div class="min-h-screen bg-[#181a1b] text-[#e8e6e3] p-4 md:p-8 font-sans flex flex-col items-center">
    <div class="w-full max-w-5xl space-y-6">
        
        <!-- HEADER -->
        <div class="flex flex-col items-center mb-8 mt-4">
            <div class="text-center text-4xl md:text-5xl font-black tracking-widest" style="font-family: 'Orbitron', sans-serif;">
                <span class="text-white">GATEKEEPER</span><span class="text-[#818cf8]">.CDR</span>
            </div>
            <div class="text-[#aaa297] text-xs md:text-sm mt-3 tracking-[2px] uppercase">
                Secure · Multi-Platform · Zero-Trust
            </div>
            <p class="text-[#8888aa] text-center max-w-2xl mt-4 text-sm leading-relaxed">
                Gatekeeper is a high-performance Content Disarm and Reconstruction engine. It neutralizes steganography, exploits, and hidden payloads by stripping all metadata and completely rebuilding uploaded files from raw pixel/byte streams across 5 parallel language bindings.
            </p>
        </div>

        <!-- STATS ROW -->
        <div class="grid grid-cols-3 gap-3 md:gap-6 mb-6">
            <div class="bg-[#0a0a12] border border-[#1f2937] p-3 md:p-4 flex flex-col items-center justify-center transition-all hover:border-[#22c55e]/50">
                <div class="text-[#22c55e] text-lg md:text-xl font-bold font-mono">5 NATIVE</div>
                <div class="text-[#8888aa] text-[9px] md:text-xs tracking-[1px] mt-1">BACKENDS</div>
            </div>
            <div class="bg-[#0a0a12] border border-[#1f2937] p-3 md:p-4 flex flex-col items-center justify-center transition-all hover:border-[#818cf8]/50">
                <div class="text-[#818cf8] text-lg md:text-xl font-bold font-mono">O(1)</div>
                <div class="text-[#8888aa] text-[9px] md:text-xs tracking-[1px] mt-1">MEMORY PATHWAY</div>
            </div>
            <div class="bg-[#0a0a12] border border-[#1f2937] p-3 md:p-4 flex flex-col items-center justify-center transition-all hover:border-[#f59e0b]/50">
                <div class="text-[#f59e0b] text-lg md:text-xl font-bold font-mono">100%</div>
                <div class="text-[#8888aa] text-[9px] md:text-xs tracking-[1px] mt-1">METADATA PURGE</div>
            </div>
        </div>

        <!-- UPLOAD CARD -->
        <div class="bg-[#0a0a12] border border-[#1f2937] p-5 shadow-2xl relative">
            <div class="flex justify-between items-center mb-4">
                <div class="text-[#8888aa] text-[10px] tracking-[2px]">
                    PIPELINE STATUS
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full {loading ? 'bg-[#f59e0b] animate-pulse' : 'bg-[#22c55e]'}"></div>
                    <div class="text-[9px] tracking-[1px] {loading ? 'text-[#f59e0b]' : 'text-[#22c55e]'}">
                        {loading ? 'DISARMING PAYLOAD...' : 'READY'}
                    </div>
                </div>
            </div>

            <!-- Sleek Upload Input -->
            <div class="flex flex-col md:flex-row items-center gap-4 bg-[#12121a] border border-[#22c55e]/30 p-4 relative transition-colors {files && files.length > 0 ? 'border-[#818cf8]/50' : 'hover:border-[#22c55e]/60'}">
                <div class="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse absolute left-4 hidden md:block"></div>
                
                <div class="flex-1 md:pl-6 w-full text-center md:text-left">
                    <input type="file" id="file-upload" bind:files class="hidden" />
                    <label for="file-upload" class="cursor-pointer text-[#aaa297] text-xs md:text-sm font-mono border-b border-dashed border-[#8888aa] pb-1 hover:text-white transition-colors">
                        {files && files.length > 0 ? files[0].name : 'SELECT SUSPICIOUS FILE [TARGET]'}
                    </label>
                </div>

                <div class="flex gap-4 items-center justify-between w-full md:w-auto">
                    {#if files && files.length > 0}
                        <div class="text-[#aaa297] text-xs font-mono">
                            {(files[0].size / 1024).toFixed(1)} KB
                        </div>
                    {/if}
                    <button 
                        onclick={handleUpload}
                        disabled={!files || loading}
                        class="px-6 py-2 text-xs font-bold tracking-widest uppercase transition-all duration-300 border {files && !loading ? 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e] hover:bg-[#22c55e]/20 hover:scale-[1.02]' : 'bg-transparent text-[#1f2937] border-[#1f2937] cursor-not-allowed'}"
                    >
                        {loading ? 'EXECUTING' : 'INITIATE'}
                    </button>
                </div>
            </div>
        </div>

        {#if error}
            <div class="bg-[#ef4444]/10 border border-[#ef4444] p-4 flex items-start gap-3">
                <div class="w-2 h-2 rounded-full bg-[#ef4444] mt-1.5"></div>
                <div>
                    <div class="text-[#ef4444] text-[10px] tracking-[2px] mb-1">SYSTEM ERROR</div>
                    <div class="text-[#ef4444]/80 text-sm font-mono break-all">{error}</div>
                </div>
            </div>
        {/if}

        {#if currentOriginalSrc}
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6 items-start">
                
                <!-- ORIGINAL IMAGE -->
                <div class="bg-[#0a0a12] border border-[#1f2937] sticky top-6">
                    <div class="flex justify-between items-center border-b border-[#1f2937] p-3 md:p-4">
                        <span class="text-[#8888aa] text-[10px] tracking-[2px]">RAW PAYLOAD [DANGER]</span>
                        <span class="text-[#ef4444] text-xs font-mono">{(currentOriginalSize / 1024).toFixed(1)} KB</span>
                    </div>
                    <div class="p-4 flex justify-center bg-[#12121a] m-3 border border-[#ef4444]/20">
                        <img src={currentOriginalSrc} alt="Original" class="max-w-full max-h-[500px] object-contain opacity-90" />
                    </div>
                </div>

                <!-- RESULTS FEED -->
                <div class="space-y-4">
                    {#if loading && results.length === 0}
                        <div class="bg-[#0a0a12] border border-[#1f2937] p-12 flex flex-col items-center justify-center gap-4">
                            <div class="w-8 h-8 border-2 border-t-[#818cf8] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                            <div class="text-[#818cf8] text-xs font-mono animate-pulse">PROCESSING THROUGH 5 ENGINES...</div>
                        </div>
                    {/if}
                    
                    {#each results as res (res.id)}
                    <div class="bg-[#0a0a12] border border-[#1f2937] transition-all hover:border-[#22c55e]/40 relative">
                        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center border-b border-[#1f2937] p-3 md:p-4 gap-2">
                            <span class="text-[#22c55e] text-[10px] tracking-[2px] font-bold flex items-center gap-2">
                                <div class="w-1.5 h-1.5 rounded-full bg-[#22c55e]"></div>
                                SANITIZED BY {res.backendName.toUpperCase()}
                            </span>
                            
                            <div class="flex items-center gap-4 text-xs font-mono">
                                <div class="text-[#aaa297]">
                                    <span class="text-[#8888aa]">OUT:</span> {(res.finalSize / 1024).toFixed(1)} KB
                                </div>
                                {#if res.finalSize <= res.originalSize}
                                    <div class="text-[#22c55e] bg-[#22c55e]/10 px-2 py-0.5 rounded-sm">
                                        -{(((res.originalSize - res.finalSize) / res.originalSize) * 100).toFixed(1)}%
                                    </div>
                                {:else}
                                    <div class="text-[#f59e0b] bg-[#f59e0b]/10 px-2 py-0.5 rounded-sm">
                                        +{(((res.finalSize - res.originalSize) / res.originalSize) * 100).toFixed(1)}%
                                    </div>
                                {/if}
                            </div>
                        </div>
                        
                        {#if res.imageSrc}
                            <div class="p-4 bg-[#12121a] m-3 border border-[#22c55e]/20 grid grid-cols-2 gap-4">
                                <div class="flex flex-col items-center">
                                    <div class="text-[#8888aa] text-[10px] tracking-[2px] mb-2 uppercase">NATIVE: {res.outputFormat}</div>
                                    <img src={res.imageSrc} alt="Native Sanitized by {res.backendName}" class="max-w-full max-h-[500px] object-contain" />
                                </div>
                                {#if res.pngImageSrc}
                                    <div class="flex flex-col items-center border-l border-[#1f2937] pl-4">
                                        <div class="text-[#818cf8] text-[10px] tracking-[2px] mb-2 uppercase">ZERO-TRUST: PNG</div>
                                        <img src={res.pngImageSrc} alt="Lossless PNG by {res.backendName}" class="max-w-full max-h-[500px] object-contain" />
                                    </div>
                                {:else}
                                    <div class="flex flex-col items-center justify-center border-l border-[#1f2937] pl-4">
                                        <div class="text-[#ef4444] text-[10px] tracking-[2px] mb-2 uppercase">PNG UNAVAILABLE</div>
                                        <div class="text-[#8888aa] text-xs font-mono text-center px-4">Backend did not return a zero-trust PNG version for this format.</div>
                                    </div>
                                {/if}
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
    :global(body) {
        background-color: #181a1b;
        color: #e8e6e3;
        margin: 0;
    }
</style>
