import React from "react";
import { RotatingLines } from "react-loader-spinner";

export const LoadingPage = () => {
  return (
    <div className="loading-page" style={{background:"white",zIndex:"9999",width:"100%",height:"100vh"}}>
      <div style={{position:"absolute",left:"50%",right:"50%",top:"50%"}}>
      <RotatingLines
        strokeColor="grey"
        strokeWidth="5"
        animationDuration="0.75"
        width="96"
        visible={true}
      />
      </div>
      
    </div>
    
  );
}