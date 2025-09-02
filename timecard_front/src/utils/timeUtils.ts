
export const toLocalDateTimeString = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
};

export const showTimeDifference = (start: Date, end: Date) => {
  let diff = Math.abs(start.getTime() - end.getTime());
  diff = diff / 1000;
  const hours = Math.floor(diff / 3600);
  if (hours) { diff = diff - hours * 3600; }

  const minutes = Math.floor(diff / 60);
  if (minutes) { diff = diff - minutes * 60 }

  if (hours) {
    return `${hours}hr${minutes ? ' ' + minutes.toString() + 'min' : ''}`;
  }
  return `${minutes} min`
}

export const timeDiff = (start: Date, end: Date) => {
  const diff = Math.abs(start.getTime() - end.getTime());
  return diff;
}

export const showTime = (ms: number) => {
  let sec = ms / 1000;
  const hours = Math.floor(sec / 3600);
  if (hours) { sec = sec - hours * 3600; }

  const minutes = Math.floor(sec / 60);
  if (minutes) { sec = sec - minutes * 60 }

  if (hours) {
    return `${hours}hr${minutes ? ' ' + minutes.toString() + 'min' : ''}`;
  }
  return `${minutes} min`

}
