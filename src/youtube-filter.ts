// YouTube AI Filter - Working version with loading screen
console.log('YouTube Filter v5: Starting...');

const config = {
  PROJECT_ID: 'your-gcp-project-id',
  FILTER_VIDEO_URL: 'https://us-central1-your-gcp-project-id.cloudfunctions.net/filter_video'
};

if (window.location.hostname === 'www.youtube.com') {
  console.log('YouTube Filter v5: Detected YouTube!');
  
  let userPreferences = '';
  let processedVideos = new Set<string>();
  let loadingScreen: HTMLElement | null = null;
  let isFirstLoad = true;
  let hasReceivedFirstResponse = false;
  let currentMessage = 0; // 0 = "blocking the junk", 1 = "preparing the page"
  let videosToProcessForLoading = 10; // Number of videos to process before removing loading screen
  let loadingVideoResponses = 0; // Counter for responses received during loading
  
  // Load preferences
  chrome.storage.local.get(['userPreferences'], (result) => {
    userPreferences = result.userPreferences || '';
    console.log('YouTube Filter v4: Preferences loaded:', userPreferences);
    
    // Reset block counter on initial load
    if (window.location.pathname === '/' || window.location.pathname === '/feed/trending') {
      chrome.storage.local.set({ blockedVideosCount: 0 });
      console.log('YouTube Filter v5: Block counter reset to 0 on initial load');
    }
    
    if (userPreferences) {
      startFiltering();
    }
  });
  
  // Listen for preference changes
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.userPreferences) {
      userPreferences = changes.userPreferences.newValue || '';
      processedVideos.clear();
      hasReceivedFirstResponse = false;
      loadingVideoResponses = 0;
      
      // Reset block counter when preferences change
      if (window.location.pathname === '/' || window.location.pathname === '/feed/trending') {
        chrome.storage.local.set({ blockedVideosCount: 0 });
        console.log('YouTube Filter v5: Block counter reset to 0 on preference change');
      }
      
      console.log('YouTube Filter v5: Preferences updated:', userPreferences);
      if (userPreferences) {
        startFiltering();
      }
    }
  });

  // Listen for page navigation to detect reloads
  let currentUrl = window.location.href;
  const urlObserver = new MutationObserver(() => {
    if (window.location.href !== currentUrl) {
      currentUrl = window.location.href;
      if (window.location.pathname === '/' || window.location.pathname === '/feed/trending') {
        console.log('YouTube Filter v5: Page navigation detected, resetting first load and block counter');
        isFirstLoad = true;
        hasReceivedFirstResponse = false;
        loadingVideoResponses = 0;
        
        // Reset block counter on home page reload
        chrome.storage.local.set({ blockedVideosCount: 0 });
        console.log('YouTube Filter v5: Block counter reset to 0');
        
        if (userPreferences) {
          startFiltering();
        }
      }
    }
  });
  urlObserver.observe(document.body, { childList: true, subtree: true });

  function createLoadingScreen() {
    if (loadingScreen) return;
    
    console.log('YouTube Filter v5: Creating loading screen');
    
    // Disable scrolling
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    
    loadingScreen = document.createElement('div');
    loadingScreen.id = 'youtube-ai-loading';
    loadingScreen.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.9);
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      z-index: 999999;
      color: white;
      font-family: 'YouTube Sans', Roboto, Arial, sans-serif;
    `;

    // Create spinner
    const spinner = document.createElement('div');
    spinner.style.cssText = `
      width: 50px;
      height: 50px;
      border: 4px solid rgba(255, 255, 255, 0.3);
      border-top: 4px solid #ff0000;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 20px;
    `;

    // Add spinner animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);

    // Create message text
    const messageText = document.createElement('div');
    messageText.id = 'loading-message';
    messageText.style.cssText = `
      font-size: 18px;
      font-weight: 500;
      text-align: center;
      letter-spacing: 0.5px;
    `;
    messageText.textContent = getLoadingMessage();

    loadingScreen.appendChild(spinner);
    loadingScreen.appendChild(messageText);
    document.body.appendChild(loadingScreen);

    // Alternate messages every 2 seconds
    const messageInterval = setInterval(() => {
      if (!loadingScreen) {
        clearInterval(messageInterval);
        return;
      }
      currentMessage = 1 - currentMessage; // Toggle between 0 and 1
      const msgElement = document.getElementById('loading-message');
      if (msgElement) {
        msgElement.textContent = getLoadingMessage();
      }
    }, 2000);
  }

  function getLoadingMessage(): string {
    return currentMessage === 0 ? 'Blocking the junk...' : 'Preparing the page...';
  }

  function removeLoadingScreen() {
    if (loadingScreen) {
      console.log('YouTube Filter v5: Removing loading screen');
      loadingScreen.remove();
      loadingScreen = null;
      
      // Re-enable scrolling
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
    }
  }
  
  function startFiltering() {
    console.log('YouTube Filter v5: Starting video filtering...');
    
    // Show loading screen on first load or reload
    if (isFirstLoad && !hasReceivedFirstResponse) {
      createLoadingScreen();
    }
    
    // Process existing videos
    setTimeout(processVideos, 3000);
    // Then check periodically for new videos
    setInterval(processVideos, 5000);
  }
  
  function processVideos() {
    if (!userPreferences) return;
    
    console.log('YouTube Filter v5: Processing videos...');
    
    // Use the working selector we found
    const allContainers = document.querySelectorAll('ytd-rich-item-renderer');
    console.log(`YouTube Filter v5: Found ${allContainers.length} total containers`);
    
    // Filter out ad containers and keep only actual video containers
    const videoContainers = Array.from(allContainers).filter(container => {
      const hasAdSlot = container.querySelector('ytd-ad-slot-renderer');
      const hasVideoContent = container.querySelector('ytd-rich-grid-media, #dismissible');
      console.log(`YouTube Filter v5: Container has ad slot: ${!!hasAdSlot}, has video content: ${!!hasVideoContent}`);
      return !hasAdSlot && hasVideoContent;
    });
    
    console.log(`YouTube Filter v5: Found ${videoContainers.length} actual video containers (filtered out ads)`);
    
    // If loading screen is active, process the first 6 videos
    // Otherwise, process all videos
    const containersToProcess = loadingScreen ? videoContainers.slice(0, videosToProcessForLoading) : videoContainers;
    
    if (loadingScreen) {
      console.log(`YouTube Filter v5: Loading screen active, processing first ${videosToProcessForLoading} videos (${containersToProcess.length} available)`);
    }
    
    containersToProcess.forEach((container, index) => {
      try {
        console.log(`YouTube Filter v5: Checking container ${index + 1}/${containersToProcess.length}`);
        
        // Find title in this container
        console.log(`YouTube Filter v5: Container HTML structure:`, container.innerHTML.substring(0, 500));
        
        // Try multiple selectors to find title
        let titleElement = container.querySelector('a#video-title');
        if (!titleElement) titleElement = container.querySelector('#video-title');
        if (!titleElement) titleElement = container.querySelector('h3 a');
        if (!titleElement) titleElement = container.querySelector('[id*="video-title"]');
        if (!titleElement) titleElement = container.querySelector('a[title]');
        if (!titleElement) titleElement = container.querySelector('yt-formatted-string');
        if (!titleElement) titleElement = container.querySelector('a span');
        
        if (!titleElement) {
          console.log(`YouTube Filter v5: No title element found in container ${index + 1} with any selector`);
          console.log(`YouTube Filter v5: Available links:`, Array.from(container.querySelectorAll('a')).map(a => a.textContent?.trim()).filter(Boolean));
          return;
        }
        
        console.log(`YouTube Filter v5: Found title element:`, titleElement.tagName, titleElement.className, titleElement.id);
        
        if (!titleElement.textContent) {
          console.log(`YouTube Filter v5: Title element found but no text content in container ${index + 1}`);
          return;
        }
        
        const title = titleElement.textContent.trim();
        console.log(`YouTube Filter v5: Found title: "${title}"`);
        
        // Use the index from the filtered video containers list
        const actualIndex = videoContainers.indexOf(container);
        const videoId = `video_${actualIndex}_${title.substring(0, 30)}`;
        console.log(`YouTube Filter v5: Generated videoId: ${videoId}`);
        
        // Skip if already processed
        if (processedVideos.has(videoId)) {
          console.log(`YouTube Filter v5: Video already processed: ${videoId}`);
          return;
        }
        
        console.log(`YouTube Filter v5: Processing "${title}"`);
        processedVideos.add(videoId);
        
        // Make API call
        fetch(config.FILTER_VIDEO_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: title,
            preferences: userPreferences
          })
        })
        .then(response => response.json())
        .then(data => {
          console.log(`YouTube Filter v5: Decision for "${title}": ${data.decision}`);
          
          // Count responses if loading screen is active
          if (loadingScreen) {
            loadingVideoResponses++;
            console.log(`YouTube Filter v5: Received response ${loadingVideoResponses}/${videosToProcessForLoading} during loading`);
            
            // Remove loading screen after receiving responses for first 6 videos
            if (loadingVideoResponses >= videosToProcessForLoading) {
              hasReceivedFirstResponse = true;
              isFirstLoad = false;
              removeLoadingScreen();
              console.log(`YouTube Filter v5: Received all ${videosToProcessForLoading} responses, removing loading screen`);
            }
          }
          
          if (data.decision === 'remove') {
            blurVideo(container as HTMLElement, title);
          }
        })
        .catch(error => {
          console.error('YouTube Filter v5: API Error:', error);
          
          // Count errors as responses too if loading screen is active
          if (loadingScreen) {
            loadingVideoResponses++;
            console.log(`YouTube Filter v5: Received error response ${loadingVideoResponses}/${videosToProcessForLoading} during loading`);
            
            // Remove loading screen after receiving responses for first 6 videos (including errors)
            if (loadingVideoResponses >= videosToProcessForLoading) {
              hasReceivedFirstResponse = true;
              isFirstLoad = false;
              removeLoadingScreen();
              console.log(`YouTube Filter v5: Received all ${videosToProcessForLoading} responses (including errors), removing loading screen`);
            }
          }
        });
        
      } catch (error) {
        console.error('YouTube Filter v5: Processing error:', error);
      }
    });
  }
  
  function blurVideo(element: HTMLElement, title: string) {
    console.log(`YouTube Filter v5: Blurring "${title}"`);
    
    // Increment blocked videos counter
    chrome.storage.local.get(['blockedVideosCount'], (result) => {
      const currentCount = result.blockedVideosCount || 0;
      chrome.storage.local.set({ blockedVideosCount: currentCount + 1 });
      console.log(`YouTube Filter v5: Blocked videos count updated to ${currentCount + 1}`);
    });
    
    // Apply blur effect
    element.style.filter = 'blur(5px)';
    element.style.opacity = '0.6';
    element.style.transition = 'filter 0.3s ease, opacity 0.3s ease';
    
    // Add hover effects
    element.addEventListener('mouseenter', () => {
      element.style.filter = 'blur(2px)';
      element.style.opacity = '0.8';
    });
    
    element.addEventListener('mouseleave', () => {
      element.style.filter = 'blur(5px)';
      element.style.opacity = '0.6';
    });
    
    // Add overlay
    const overlay = document.createElement('div');
    overlay.textContent = 'Filtered by AI';
    overlay.style.position = 'absolute';
    overlay.style.top = '10px';
    overlay.style.left = '10px';
    overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.9)';
    overlay.style.color = 'white';
    overlay.style.padding = '8px 12px';
    overlay.style.fontSize = '12px';
    overlay.style.fontWeight = 'bold';
    overlay.style.borderRadius = '4px';
    overlay.style.zIndex = '1000';
    overlay.style.pointerEvents = 'none';
    
    if (element.style.position !== 'relative') {
      element.style.position = 'relative';
    }
    element.appendChild(overlay);
  }
}