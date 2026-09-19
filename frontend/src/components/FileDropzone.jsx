import { useRef, useState } from 'react'
import { FileImage, UploadCloud } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'

export default function FileDropzone({ files, onChange }) {
  const { t } = useTranslation()
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files.length) {
      onChange(Array.from(e.dataTransfer.files))
    }
  }

  return (
    <div
      className={`dropzone${dragOver ? ' dragover' : ''}`}
      onClick={() => inputRef.current?.click()}
      onDragEnter={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragOver={(e) => e.preventDefault()}
      onDragLeave={(e) => {
        e.preventDefault()
        setDragOver(false)
      }}
      onDrop={handleDrop}
    >
      {files.length ? <FileImage /> : <UploadCloud />}
      {files.length ? (
        <span className="filename">{files.map((f) => f.name).join(', ')}</span>
      ) : (
        <span>{t('dropzone.hint')}</span>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*,.pdf"
        multiple
        onChange={(e) => onChange(Array.from(e.target.files))}
      />
    </div>
  )
}
