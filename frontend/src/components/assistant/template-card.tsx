import { FileText, Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { AssistantTemplate } from '@/types'

interface TemplateCardProps {
  template: AssistantTemplate
  onUse: () => void
  isLoading?: boolean
}

export function TemplateCard({ template, onUse, isLoading }: TemplateCardProps) {
  return (
    <Card className="group transition-shadow hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold">{template.name}</h3>
              <Badge variant="secondary" className="mt-1">
                {template.category}
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
          {template.description}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {template.model.split('/').pop()}
          </span>
          <Button
            size="sm"
            onClick={onUse}
            disabled={isLoading}
          >
            <Sparkles className="h-4 w-4 mr-1" />
            Use Template
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
