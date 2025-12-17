import React from 'react'
import './Loading.css'

/**
 * Loading Component - Loading spinner and states
 * @param {string} size - 'sm' | 'md' | 'lg'
 * @param {string} variant - 'spinner' | 'dots' | 'skeleton'
 * @param {string} text - Loading text
 */
export const Loading = ({
  size = 'md',
  variant = 'spinner',
  text,
  className = '',
}) => {
  if (variant === 'skeleton') {
    return <div className={`ui-skeleton ${className}`} />
  }

  return (
    <div className={`ui-loading ui-loading--${size} ${className}`}>
      {variant === 'spinner' && <div className="ui-spinner" />}
      {variant === 'dots' && (
        <div className="ui-dots">
          <span />
          <span />
          <span />
        </div>
      )}
      {text && <span className="ui-loading-text">{text}</span>}
    </div>
  )
}

/**
 * Loading Overlay - Full screen or container overlay
 */
export const LoadingOverlay = ({ children, loading, text }) => {
  return (
    <div className="ui-loading-overlay-wrapper" style={{ position: 'relative' }}>
      {children}
      {loading && (
        <div className="ui-loading-overlay">
          <Loading text={text} />
        </div>
      )}
    </div>
  )
}

export default Loading

