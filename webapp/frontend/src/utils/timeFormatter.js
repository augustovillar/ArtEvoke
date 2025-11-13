/**
 * Convert milliseconds to HH:MM:SS format
 * @param {number} milliseconds - Time in milliseconds
 * @returns {string} Time formatted as HH:MM:SS
 */
export const millisecondsToTimeString = (milliseconds) => {
  const totalSeconds = Math.floor(milliseconds / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
};
