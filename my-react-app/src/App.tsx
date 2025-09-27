import "./App.css";
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { WebcamClient, WebEyeTrackProxy, type GazeResult } from 'webeyetrack';
import GazeDot from './GazeDot.tsx';

export default function App() {
  const [gaze, setGaze] = useState({ x: 0, y: 0, gazeState: 'closed'});
  const hasInitializedRef = useRef(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    if (hasInitializedRef.current) return;
    hasInitializedRef.current = true;

    async function startWebEyeTrack() {
      if (videoRef.current) {

        const webcamClient = new WebcamClient(videoRef.current.id);
        const webEyeTrackProxy = new WebEyeTrackProxy(webcamClient);

        // Define callback for gaze results
        webEyeTrackProxy.onGazeResults = (gazeResult: GazeResult) => {
          // Update gaze position and state
          setGaze({
            x: (gazeResult.normPog[0] + 0.5) * window.innerWidth,
            y: (gazeResult.normPog[1] + 0.5) * window.innerHeight,
            gazeState: gazeResult.gazeState
          });
        }
      }
    }

    startWebEyeTrack();
  }, []); // Empty dependency array to run only on mount/unmount

 return (
  <>
    {/* Add some debug info */}
    <div className="absolute top-0 left-0 z-50 bg-black text-white p-2">
      <p>Gaze: x={gaze.x.toFixed(0)}, y={gaze.y.toFixed(0)}</p>
      <p>State: {gaze.gazeState}</p>
    </div>

    {/* Gaze Dot */}
    <div className="absolute left-0 right-0 w-full h-full z-100 pointer-events-none">
      <GazeDot x={gaze.x} y={gaze.y} gazeState={gaze.gazeState}/>
    </div>

    {/* Video Element - make it visible for debugging */}
    <video
      id='webcam'
      ref={videoRef}
      autoPlay
      playsInline
      style={{ width: '200px', height: '150px', position: 'absolute', bottom: 0, right: 0 }}
    />
  </>
  );
}