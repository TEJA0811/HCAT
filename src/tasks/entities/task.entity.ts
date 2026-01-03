import { TaskDifficulty, TaskStatus, UserType } from '../../utils/constant';
import { Entity, PrimaryGeneratedColumn, Column, BaseEntity, ManyToOne, JoinColumn, ManyToMany, CreateDateColumn } from 'typeorm';
import { Project } from '../../projects/entities/project.entity';
import { Manager } from '../../managers/entities/manager.entity';
import { User } from '../../users/entities/user.entity';

@Entity({ name: 'tasks' })
export class Task extends BaseEntity {
  @PrimaryGeneratedColumn({ type: 'bigint' })
  id: number;

  @Column({ length: 70 })
  title: string;

  @Column()
  description: string;

  @Column({ type: 'bigint', nullable: true})
  assignee_id: number;

  @Column({ type: 'int', nullable: true })
  story_points: number;

  @Column({ type: 'varchar', nullable: true })
  sprint: string; 

  @Column({ type: 'date', nullable: true })
  deadline: Date;

  @Column({ type: 'bigint', nullable: true })
  project_id: number;

   @Column({
    type: 'enum',
    enum: TaskDifficulty,
    default: TaskDifficulty.MEDIUM,
  })
  difficulty: TaskDifficulty;

  @Column({
    type: 'enum',
    enum: TaskStatus,
    default: TaskStatus.READY,
  })
  status: TaskStatus;

  @Column({ type: 'bigint' })
  assigned_by: number;

  // Many tasks belong to one project
  @ManyToOne(() => Project, (project) => project.tasks)
  @JoinColumn({ name: 'project_id' })
  project: Project;

    // Many tasks assigned by Manager
  @ManyToOne(() => Manager, (manager) => manager.assignedTasks)
  @JoinColumn({ name: 'assigned_by' })
  assignedByManager: Manager;

    // Many tasks belong to one user
  @ManyToOne(() => User, (user) => user.tasks)
  @JoinColumn({ name: 'assignee_id' })
  assignee: User;
  
}
